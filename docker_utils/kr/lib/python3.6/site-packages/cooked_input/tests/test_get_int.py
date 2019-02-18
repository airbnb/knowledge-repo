
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

from cooked_input import get_input, get_int, silent_error, log_error
from cooked_input import IntConvertor, RangeValidator, EqualToValidator
from cooked_input import NoneOfValidator, AnyOfValidator
from .utils import redirect_stdin
# from cooked_input.tests.utils import redirect_stdin   # needed this to run under main here


def my_print_error(fmt_str, value, error_content):
    print('<<< ' + fmt_str.format(value=value, error_content=error_content) + ' >>>')


class TestGetInt(object):
    int_convertor = IntConvertor()
    pos_int_validator = RangeValidator(min_val=1, max_val=None)
    zero_to_ten_validator = RangeValidator(min_val=0, max_val=10)
    exactly_0_validator = EqualToValidator(value=0)
    exactly_5_validator = EqualToValidator(value=5)
    not_0_validator = NoneOfValidator(validators=[exactly_0_validator])
    not_5_validator = NoneOfValidator(validators=[exactly_5_validator])
    in_0_or_5_validator = AnyOfValidator(validators=[exactly_0_validator, exactly_5_validator])
    not_0_or_5_validator = NoneOfValidator(validators=[exactly_0_validator, exactly_5_validator])
    convertor_fmt = '# {value} cannot be converted to {error_content} #'
    validator_fmt = '@ {value} {error_content} @'


    def test_get_input_int(self):
        input_str = u"""
            10
            5
            -1
            1
    
            """

        irv = RangeValidator(min_val=1, max_val=10)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='enter an integer (1<=x<=10)', convertor=IntConvertor(), validators=irv)
            print(result)
            assert(result==10)

            result = get_input(prompt='enter an integer (1<=x<=10)', convertor=IntConvertor(), validators=irv)
            print(result)
            assert(result==5)

            result = get_input(prompt='enter an integer (1<=x<=10)', convertor=IntConvertor(), validators=irv)
            print(result)
            assert(result==1)

        print(self.int_convertor)   # for code coverage


    def test_ignore_bad_conversion(self):
        input_str = u"""
            foo
            101
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='Enter an integer', convertor=IntConvertor())
            assert(result==101)


    def test_use_default_value(self):
        input_str = u"""

            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='Enter an integer', convertor=IntConvertor(), default=5)
            assert (result == 5)


    def test_get_pos_int(self):
        input_str = u"""
            -1
            0
            10
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(convertor=IntConvertor(), validators=self.pos_int_validator, prompt='Enter a positive integer')
            assert (result == 10)


    def test_get_0_to_10(self):
        input_str = u"""
            -1
            11
            0
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(convertor=self.int_convertor, validators=[self.zero_to_ten_validator],
                        prompt='Enter an integer between 0 and 10')
            assert (result == 0)


    def test_exactly_val(self):
        # get zero - silly but makes more sense with the in any or not in validators
        input_str = u"""
            1
            0
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(convertor=self.int_convertor, validators=[self.exactly_0_validator], prompt='Enter 0')
            assert (result == 0)


    def test_in_any_val(self):
        # get zero or 5
        input_str = u"""
            foo
            1
            5
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(convertor=self.int_convertor, validators=[self.in_0_or_5_validator], prompt='Enter 0 or 5')
            assert (result == 5)


    def test_not_in(self):
        # get a non-zero integer
        input_str = u"""
            0
            -101
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(convertor=self.int_convertor, validators=[self.not_0_validator], prompt='Enter a non-zero integer')
            assert (result == -101)


    def test_in_range_and_not_in(self):
        # get a non-zero integer between 0 and 10
        input_str = u"""
            0
            -1
            11
            5
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(convertor=self.int_convertor, validators=[self.zero_to_ten_validator, self.not_0_validator],
                        prompt='Enter a non-zero integer between 0 and 10')
            assert (result == 5)


    def test_mult_not_in(self):
        # enter an integer besides zero or 5
        input_str = u"""
            0
            5
            -101
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(convertor=self.int_convertor, validators=[self.not_0_or_5_validator],
                        prompt='Enter and integer besides 0 or 5')
            assert (result == -101)


    def test_error_callback(self):
        # test error callbacks and format strings
        input_str = u"""
            foo
            -1
            12
            5
            7
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(convertor=IntConvertor(), validators=[self.zero_to_ten_validator, self.not_5_validator],
                        prompt='Enter a non-zero integer between 0 and 10, but not 5 (my_print_error)',
                        error_callback=my_print_error,
                        convertor_error_fmt=self.convertor_fmt, validator_error_fmt=self.validator_fmt)
            assert (result == 7)


    def test_silent_error(self):
        input_str = u"""
            foo
            -1
            12
            5
            5
            4
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(convertor=IntConvertor(), validators=[self.zero_to_ten_validator, self.not_5_validator],
                        prompt='Enter a non-zero integer between 0 and 10, but not 5 (errors not printed)',
                        error_callback=silent_error,
                        convertor_error_fmt=self.convertor_fmt, validator_error_fmt=self.validator_fmt)
            assert (result == 4)


    def test_log_error(self):
        input_str = u"""
            foo
            -1
            12
            5
            5
            4
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(convertor=IntConvertor(), validators=[self.zero_to_ten_validator, self.not_5_validator],
                        prompt='Enter a non-zero integer between 0 and 10, but not 5 (errors not printed)',
                        error_callback=log_error)
            assert (result == 4)



    def test_get_int(self):
        input_str = u"""
            foo
            3.14
            101
            5
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_int()
            assert (result == 101)

        with redirect_stdin(StringIO(input_str)):
            result = get_int(prompt='Enter an integer')
            assert (result == 101)

        with redirect_stdin(StringIO(input_str)):
            result = get_int(validators=[self.zero_to_ten_validator],
                        error_callback=my_print_error,
                        convertor_error_fmt=self.convertor_fmt, validator_error_fmt=self.validator_fmt)
            assert (result == 5)

        with redirect_stdin(StringIO(input_str)):
            result = get_int(validators=[self.zero_to_ten_validator],
                        prompt='Enter a integer between 0 and 10',
                        error_callback=my_print_error,
                        convertor_error_fmt=self.convertor_fmt, validator_error_fmt=self.validator_fmt)
            assert (result == 5)

    def test_get_int_part2(self):
        input_str = u"""
            foo
            3.14
            101
            5
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_int(validators=self.not_0_validator, prompt='Enter an integer that is not 0')
            assert (result == 101)

        input_str = u"""
            -11
            11
            5
            """
        with redirect_stdin(StringIO(input_str)):
            result = get_int(validators=None, minimum=-10, maximum=10, prompt='Enter an integer between -10 and 10')
            assert (result == 5)

        with redirect_stdin(StringIO(input_str)):
            result = get_int(validators=None, minimum=1, prompt='Enter an integer greater than 0')
            assert (result == 11)

        with redirect_stdin(StringIO(input_str)):
            result = get_int(validators=None, maximum=10, prompt='Enter an integer less than than 11')
            assert (result == -11)

        input_str = u"""
            -11
            11
            0
            5
            6
            """
        with redirect_stdin(StringIO(input_str)):
            result = get_int(validators=None, minimum=1, maximum=10, prompt='Enter an integer between 1 and 10')
            assert (result == 5)

        with redirect_stdin(StringIO(input_str)):
            result = get_int(validators=self.not_0_validator, minimum=-10, maximum=10,
                      prompt='Enter an integer between -10 and 10, but not 0')
            assert (result == 5)

        with redirect_stdin(StringIO(input_str)):
            result = get_int(validators=[self.not_0_validator, self.not_5_validator], minimum=-10, maximum=10,
                      prompt='Enter an integer between -10 and 10, but not 0 or 5')
            assert (result == 6)