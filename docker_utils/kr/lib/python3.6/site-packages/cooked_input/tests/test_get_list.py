
"""
pytest tests for cooked_input - testing get_list2

pytest stuff
    run with:
        pytest cooked_input/

    cmd line args:
        -q <test_file_name>     - run a specific test file
    floating point stuff (https://docs.pytest.org/en/latest/builtin.html?highlight=approx#pytest.approx)
        approx()
    exception raised:
        https://docs.pytest.org/en/latest/getting-started.html#asserting-that-a-certain-exception-is-raised

Len Wanger, 2017
"""

import sys

if sys.version_info[0] > 2:  # For Python 3
    from io import StringIO
else:
    from StringIO import StringIO

from .utils import redirect_stdin

# from cooked_input import get_input, GetInput, get_list
# from cooked_input.validators import LengthValidator, ChoiceValidator, NoneOfValidator
# from cooked_input.cleaners import StripCleaner, CapitalizationCleaner, UPPER_CAP_STYLE, ALL_WORDS_CAP_STYLE
# from cooked_input.convertors import IntConvertor, YesNoConvertor


from cooked_input import GetInput, get_input, get_list
from cooked_input.cleaners import ChoiceCleaner, StripCleaner
from cooked_input.validators import LengthValidator, ChoiceValidator, NoneOfValidator, RangeValidator
from cooked_input.convertors import IntConvertor, YesNoConvertor, ListConvertor


class TestGetList(object):

    def test_list_of_str(self):
        input_str = 'foo, bar blat, gizmo\n'

        with redirect_stdin(StringIO(input_str)):
            list_input = GetInput()
            result = get_list(elem_get_input=list_input)
            assert (result == ['foo', 'bar blat', 'gizmo'])

    def test_list_of_int(self):
        input_str = '1,2,3\n'

        with redirect_stdin(StringIO(input_str)):
            get_int_list = GetInput(convertor=IntConvertor())
            result = get_list(prompt='List of integers between 3 and 5 numbers long, separated by ","', elem_get_input=get_int_list)
            assert (result == [1,2,3])

    def test_list_of_three_ints(self):
        input_str = '1,2\n1,4,6,7,9'

        with redirect_stdin(StringIO(input_str)):
            get_int_list = GetInput(convertor=IntConvertor())

            len_3_validator = RangeValidator(min_val=3, max_val=5)

            result = get_list(prompt='List of 3-5 integers (separated by ",")', elem_get_input=get_int_list,
                              validators=len_3_validator, value_error_str='list of values', )
            assert (result == [1, 4, 6, 7, 9])

    def test_list_of_three_ints(self):
        input_str = '1,2\n-1,4,6\n2,4,11\n2, 4, 10'

        not_1_3_5_validator = NoneOfValidator([1, 3, 5])
        zero_to_ten_validator = RangeValidator(0, 10)
        complex_in_input = GetInput(convertor=IntConvertor(), validators=[zero_to_ten_validator, not_1_3_5_validator])

        with redirect_stdin(StringIO(input_str)):
            result = get_list(elem_get_input=complex_in_input)
            assert (result == [2, 4, 10])

    def test_list_of_yes_no(self):
        input_str = 'y| yes| n| nyet'

        yn_get_input = GetInput(convertor=YesNoConvertor())

        with redirect_stdin(StringIO(input_str)):
            result = get_list(prompt='List of yes/no (separated by "|")', elem_get_input=yn_get_input, delimiter='|')
            assert (result == ['yes', 'yes', 'no', 'no'])

    def test_list_of_choices(self):
        input_str = 'r g b\nr g bl brown'

        colors = ['red', 'green', 'blue', 'brown']
        color_cleaner = ChoiceCleaner(colors)
        color_validator = ChoiceValidator(colors)
        color_input = GetInput(cleaners=color_cleaner, validators=color_validator)

        with redirect_stdin(StringIO(input_str)):
            result = get_list(elem_get_input=color_input, delimiter=' ')
            assert (result == ['red', 'green', 'blue', 'brown'])


    def test_list_of_lists(self):
        input_str = '0:0:0, 112:67:255, 255: 255: 128'

        sublist_elem_get_input = GetInput(convertor=IntConvertor(), validators=RangeValidator(0, 255))
        sublist_get_input = GetInput(convertor=ListConvertor(elem_get_input=sublist_elem_get_input, delimiter=":"),
                                     validators=LengthValidator(3, 3))
        list_get_input = GetInput(convertor=ListConvertor(elem_get_input=sublist_get_input))

        with redirect_stdin(StringIO(input_str)):
            result = list_get_input.get_input()
            assert (result == [[0, 0, 0], [112, 67, 255], [255, 255, 128]])


    def test_get_input_list_2(self):
        input_str = u"""
            foo, bar, blat
            1-2-3
            """

        lc = ListConvertor(delimiter='-', elem_get_input=GetInput(convertor=IntConvertor()))
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=lc)
            print(result)
            assert (result == [1,2,3])


    def test_get_input_list_3(self):
        input_str = u"""
            foo, bar
            -1,2,3
            """

        lc = ListConvertor(delimiter=None, elem_get_input=GetInput(convertor=IntConvertor()))
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=lc)
            print(result)
            assert (result == [-1, 2, 3])
