"""
cooked input examples of getting an integer values

Len Wanger, 2017
"""

from cooked_input import get_input, silent_error, log_error, get_int
from cooked_input.convertors import IntConvertor
from cooked_input.validators import RangeValidator, EqualToValidator, NoneOfValidator, AnyOfValidator


def my_print_error(fmt_str, value, error_content):
    print('<<< ' + fmt_str.format(value=value, error_content=error_content) + ' >>>')


if __name__ == '__main__':
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

    # get any integer - simplest way
    print(get_int())

    # get any integer - with a default value
    print(get_int(default=5))

    # more convenience function tests
    print(get_int(validators= NoneOfValidator(validators=0), prompt='Enter an integer that is not 0'))
    print(get_int(validators=None, minimum=-10, maximum=10, prompt='Enter an integer between -10 and 10'))
    print(get_int(validators=None, minimum=1, prompt='Enter a positive integer greater than 0'))
    print(get_int(validators=None, maximum=10, prompt='Enter an integer less than than 11'))
    print(get_int(validators=None, minimum=1, maximum=10, prompt='Enter an integer between 1 and 10'))
    print(get_int(validators=not_0_validator, minimum=-10, maximum=10, prompt='Enter an integer between -10 and 10, but not 0'))
    print(get_int(validators=in_0_or_5_validator, minimum=-10, maximum=10, prompt='Enter 0 or 5'))
    print(get_int(validators=[not_0_validator, not_5_validator], minimum=-10, maximum=10, prompt='Enter an integer between -10 and 10, but not 0 or 5'))

    # test error callbacks and format strings
    print(get_input(convertor=IntConvertor(), validators=[zero_to_ten_validator, not_5_validator],
                    prompt='Enter a non-zero integer between 0 and 10, but not 5 (my_print_error)', error_callback=my_print_error,
                    convertor_error_fmt=convertor_fmt, validator_error_fmt=validator_fmt))

    print(get_input(convertor=IntConvertor(), validators=[zero_to_ten_validator, not_5_validator],
                    prompt='Enter a non-zero integer between 0 and 10, but not 5 (errors not printed)', error_callback=silent_error,
                    convertor_error_fmt=convertor_fmt, validator_error_fmt=validator_fmt))

    print(get_input(convertor=IntConvertor(), validators=[zero_to_ten_validator, not_5_validator],
                    prompt='Enter an integer between 0 and 10, but not 5 (errors logged)', error_callback=log_error,
                    convertor_error_fmt=convertor_fmt, validator_error_fmt=validator_fmt))