
"""
pytest tests for cooked_input

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

from cooked_input import get_input, get_string
from cooked_input.validators import LengthValidator, ChoiceValidator, NoneOfValidator
from cooked_input.cleaners import StripCleaner, CapitalizationCleaner, UPPER_CAP_STYLE, ALL_WORDS_CAP_STYLE
from cooked_input.convertors import YesNoConvertor


class TestGetStr(object):

    def test_simple_str(self):
        input_str = 'foo\n\n'

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='Enter any string')
            assert (result == 'foo')

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='Enter any string', required=True)
            assert (result == 'foo')

            result = get_input(prompt='Enter any string', required=False)
            assert (result is None)


    def test_get_string(self):
        input_str = 'foo\n\nbar\nblat\n\nGo\n'

        with redirect_stdin(StringIO(input_str)):
            result = get_string(prompt='Enter any string', required=True)
            assert (result == 'foo')

            result = get_string(prompt='Enter any string at least 3 letters long', min_len=3, required=True)
            assert (result == 'bar')

            result = get_string(prompt='Enter any string at least 3 letters long', max_len=3, required=True)
            assert (result == 'Go')


        with redirect_stdin(StringIO(input_str)):
            result = get_string(prompt='Enter any string less than 4 letters long', max_len=3, required=True)
            assert (result == 'foo')

            result = get_string(prompt='Enter any string less than 4 letters long', min_len=2, max_len=3, required=True)
            assert (result == 'bar')

            result = get_string(prompt='Enter any string less than 4 letters long', max_len=3, required=False)
            assert (result == None)


    def test_capitalize(self):
        input_str = '  \t  bOb JoNeS\t  \t '

        strip_cleaner = StripCleaner()
        rstrip_cleaner = StripCleaner(lstrip=False, rstrip=True)
        lower_cleaner = CapitalizationCleaner(style='lower')
        upper_cleaner = CapitalizationCleaner(style=UPPER_CAP_STYLE)
        strip_and_lower_cleaners = [strip_cleaner, lower_cleaner]
        capitalize_cleaner = CapitalizationCleaner(style='capitalize')
        capitalize_all_cleaner = CapitalizationCleaner(style=ALL_WORDS_CAP_STYLE)

        with redirect_stdin(StringIO(input_str)):
            result = get_input(
                prompt='Enter any string (will be stripped of leading and trailing spaces and converted to lower)',
                cleaners=strip_and_lower_cleaners)
            assert (result == 'bob jones')

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='Enter any string (will be stripped of trailing spaces and converted to upper)',
                               cleaners=[rstrip_cleaner, upper_cleaner])
            assert (result == '  \t  BOB JONES')

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='Enter your name (first word will be capitalized)', cleaners=[strip_cleaner, capitalize_cleaner])
            assert (result == 'Bob jones')

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='Enter your name (all words will be capitalized)',
                               cleaners=[strip_cleaner, capitalize_all_cleaner])
            assert (result == 'Bob Jones')

    def test_choices(self):
        input_str_blank = """
 
            """

        input_str = """licorice
            booger
            lemon 
            """

        colors = ['red', 'green', 'blue']
        good_flavors = ['cherry', 'lime', 'lemon', 'orange']
        bad_flavors = 'licorice'
        choices_validator = ChoiceValidator(choices=colors)
        good_flavor_validator = ChoiceValidator(choices=good_flavors)
        bad_flavor_validator = ChoiceValidator(choices=bad_flavors)
        not_in_choices_validator = NoneOfValidator(validators=[bad_flavor_validator])
        strip_cleaner = StripCleaner()
        lower_cleaner = CapitalizationCleaner()
        strip_and_lower_cleaners = [strip_cleaner, lower_cleaner]

        with redirect_stdin(StringIO(input_str_blank)):
            result = get_input(cleaners=strip_and_lower_cleaners, validators=not_in_choices_validator, default='cherry')
            assert (result == 'cherry')

        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=strip_and_lower_cleaners, validators=not_in_choices_validator, default='cherry')
            assert (result == 'booger')

        with redirect_stdin(StringIO(input_str)):
            validators = [good_flavor_validator, not_in_choices_validator]
            result = get_input(cleaners=strip_and_lower_cleaners, validators=validators,default='cherry')
            assert (result == 'lemon')

    def test_choices_2(self):
        input_str_blank = """

            """

        input_str = """
                    a
                    licorice
                    bo
                    lem 
                    """

        length_3_validator = LengthValidator(min_len=3, max_len=3)
        length_5_plus_validator = LengthValidator(min_len=5)
        length_2_to_4_validator = LengthValidator(min_len=2, max_len=4)
        strip_and_lower_cleaners = [StripCleaner(), CapitalizationCleaner('lower')]

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='Enter a three letter string', cleaners=strip_and_lower_cleaners, validators=[length_3_validator])
            assert (result == 'lem')

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='Enter a string at least 5 letters long', cleaners=strip_and_lower_cleaners, validators=[length_5_plus_validator])
            assert (result == 'licorice')

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='Enter a 2 to 4 letter string', cleaners=strip_and_lower_cleaners, validators=[length_2_to_4_validator])
            assert (result == 'bo')

    def test_choices_3(self):
        input_str_blank = "\n\n"

        input_str_y = " a\ny"

        input_str_n = "a\n  no"

        strip_cleaner = StripCleaner()


        with redirect_stdin(StringIO(input_str_y)):
            result = get_input(cleaners=strip_cleaner, convertor=YesNoConvertor(), default='Y')
            assert (result == 'yes')

        with redirect_stdin(StringIO(input_str_blank)):
            result = get_input(cleaners=strip_cleaner, convertor=YesNoConvertor(), default='Y')
            assert (result == 'yes')

        with redirect_stdin(StringIO(input_str_n)):
            result = get_input(cleaners=strip_cleaner, convertor=YesNoConvertor(), default='Y')
            assert (result == 'no')