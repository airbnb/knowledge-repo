
"""
pytest tests for cooked_input floating point numbers

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

from pytest import approx

from cooked_input import get_input, get_float, FloatConvertor
from cooked_input import RangeValidator, EqualToValidator, NoneOfValidator, AnyOfValidator
from .utils import redirect_stdin
# from cooked_input.tests.utils import redirect_stdin   # needed this to run under main here


class TestGetFloat(object):
    float_convertor = FloatConvertor()

    # pos_float_validator = RangeValidator(min_val=0.0, max_val=None)
    # zero_to_ten_validator = RangeValidator(min_val=0.0, max_val=10.0)
    exactly_0_validator = EqualToValidator(value=0.0)
    exactly_512_validator = EqualToValidator(value=5.12)
    not_0_validator = NoneOfValidator(validators=[exactly_0_validator])
    not_512_validator = NoneOfValidator(validators=[exactly_512_validator])
    # in_0_or_5_validator = AnyOfValidator(validators=[exactly_0_validator, exactly_5_validator])
    # not_0_or_5_validator = NoneOfValidator(validators=[exactly_0_validator, exactly_5_validator])

    def test_get_input_float(self):
        input_str = u"""
            10
            5.1
            foo
            -1.1
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='enter a float', convertor=self.float_convertor)
            assert(result==approx(10))

            result = get_input(prompt='enter a float', convertor=self.float_convertor)
            assert(result==approx(5.1))

            result = get_input(prompt='enter a float', convertor=self.float_convertor)
            assert(result==approx(-1.1))

        print(self.float_convertor) # for code coverage


    def test_get_float(self):
        input_str = u"""
            foo
            3.14
            101
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_float()
            assert (result == approx(3.14))

            result = get_float(prompt='Enter an float')
            assert (result == approx(101.0))

    def test_get_float_part2(self):
        input_str = u"""
            foo
            0.0
            3.14
            101
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_float(validators=self.not_0_validator, prompt='Enter an float that is not 0')
            assert (result == approx(3.14))

        input_str = u"""
            -12
            10.001
            0.0
            10.000000000001
            101
            8.71
            """
        with redirect_stdin(StringIO(input_str)):
            result = get_float(validators=None, minimum=-10.0, maximum=10.0, prompt='Enter an float between -10.0 and 10.0')
            assert (result == approx(0.0))

        with redirect_stdin(StringIO(input_str)):
            result = get_float(validators=None, minimum=1., prompt='Enter an float greater than 0')
            assert (result == approx(10.001))

        with redirect_stdin(StringIO(input_str)):
            result = get_float(validators=None, maximum=10., prompt='Enter an float less than than 10.0')
            assert (result == approx(-12.0))

        with redirect_stdin(StringIO(input_str)):
            result = get_float(validators=None, minimum=0.05, maximum=10.0, prompt='Enter an float between 1 and 10')
            assert (result == approx(8.71))

        input_str = u"""
            -12
            10.001
            0.0
            5.12
            10.000000000001
            101
            8.71
            """
        with redirect_stdin(StringIO(input_str)):
            result = get_float(validators=self.not_0_validator, minimum=-10, maximum=10,
                      prompt='Enter an float between -10.0 and 10.0, but not 0')
            assert (result == approx(5.12))

        with redirect_stdin(StringIO(input_str)):
            result = get_float(validators=[self.not_0_validator, self.not_512_validator], minimum=-10, maximum=10,
                      prompt='Enter an float between -10 and 10, but not 0 or 5.12')
            assert (result == approx(8.71))


# if __name__ == '__main__':
#     c = TestCleaners()
#     c.test_get_float()