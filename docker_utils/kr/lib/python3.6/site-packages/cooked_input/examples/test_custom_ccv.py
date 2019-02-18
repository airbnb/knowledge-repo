"""
Example code showing how to create custome cooked_input cleaners, convertors and validators

Len Wanger, 9/3/2018
"""

from cooked_input import *


class Interval(object):
    def __init__(self, min_val, max_val):
        # Interval is a complex number with the minimum and maximum values in the real imaginary parts respectively
        self.interval = complex(min_val, max_val)


class IntervalConvertor(Convertor):
    def __init__(self, value_error_str='a range of numbers("x:y")'):
        super(IntervalConvertor, self).__init__(value_error_str)

    def __call__(self, value, error_callback, convertor_fmt_str):
        # interval is of the format "min : max"
        use_val = value.strip()
        dash_idx = use_val.find(':')

        if dash_idx == -1:  # No ":" was found to separate the min and max values
            error_callback(convertor_fmt_str, value, 'an interval -- ":" not found between the minimum and maximum values')
            raise ConvertorError
        else:
            try:
                min_val = int(value[:dash_idx])
            except (IndexError, TypeError, ValueError):
                error_callback(convertor_fmt_str, value, 'an interval -- invalid minimum value')
                raise ConvertorError

            try:
                max_val = int(value[dash_idx + 1:])
            except (IndexError, TypeError, ValueError):
                error_callback(convertor_fmt_str, value, 'an interval -- invalid maximum value')
                raise ConvertorError

        if min_val > max_val:
            error_callback(convertor_fmt_str, value, 'an interval -- the low value is higher than the high value')
            raise ConvertorError

        return Interval(min_val, max_val)


class IntervalValidator(Validator):
    # Validate an interval is within a specified range (min_val, max_val).
    def __init__(self, range_interval):
        # range_interval specifies the minimum and maximum values allowed for the interval to be valid
        self.range = range_interval

    def __call__(self, value, error_callback, validator_fmt_str):
        if not isinstance(value, Interval):
            error_callback(validator_fmt_str, value, 'Not an interval')
            return False

        if value.interval.real < self.range.interval.real:
            err_string = 'Low end of the interval is below the minimum ({})'.format(self.range.interval.real)
            error_callback(validator_fmt_str, value.interval.real, err_string)
            return False

        if value.interval.imag > self.range.interval.imag:
            err_string = 'High end of the interval is above the maximum ({})'.format(self.range.interval.imag)
            error_callback(validator_fmt_str, value.interval.imag, err_string)
            return False

        return True


if __name__ == '__main__':
    interval_convertor = IntervalConvertor()
    interval_validator = IntervalValidator(Interval(1, 100))
    prompt = 'Enter an interval between 1 and 100'

    int_gi = get_input(prompt=prompt, convertor=interval_convertor, validators=[interval_validator])

