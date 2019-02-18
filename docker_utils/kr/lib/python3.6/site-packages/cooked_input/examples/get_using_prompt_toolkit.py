"""
cooked input examples of getting an integer values using prompt toolket

Len Wanger, 2017
"""

from prompt_toolkit.key_binding.defaults import load_key_bindings_for_prompt
from prompt_toolkit.keys import Keys

from cooked_input import get_input, GetInputInterrupt
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

    registry = load_key_bindings_for_prompt()

    @registry.add_binding(Keys.ControlD)
    def _(event):
        event.cli.current_buffer.insert_text('Dumbo')

    @registry.add_binding(Keys.F1)
    def _(event):
        # When F1 is hit print a help message
        def get_help_text():
            print('F1 for help, Ctrl-D to add "Dumbo" to the command line')
        event.cli.run_in_terminal(get_help_text)


    print('Not using prompt_toolkit')
    print(get_input(convertor=IntConvertor(), validators=[zero_to_ten_validator, not_5_validator],
                    prompt='Enter a non-zero integer between 0 and 10, but not 5',
                    convertor_error_fmt=convertor_fmt, validator_error_fmt=validator_fmt, 
                    use_prompt_toolkit=False) )

    print('Using prompt_toolkit with default key registry (try Ctrl-D)')
    try:
        print(get_input(convertor=IntConvertor(), validators=[zero_to_ten_validator, not_5_validator],
                    prompt='Enter a non-zero integer between 0 and 10, but not 5',
                    convertor_error_fmt=convertor_fmt, validator_error_fmt=validator_fmt, 
                    use_prompt_toolkit=True) )
    except GetInputInterrupt:
        print('caught Ctrl-D!')

    print('Using prompt_toolkit with custom key registry (try F1 and Ctrl-D)')
    print(get_input(convertor=IntConvertor(), validators=[zero_to_ten_validator, not_5_validator],
                    prompt='Enter a non-zero integer between 0 and 10, but not 5',
                    convertor_error_fmt=convertor_fmt, validator_error_fmt=validator_fmt, 
                    use_prompt_toolkit=True, key_registry=registry) )

    print('Using prompt_toolkit with bottom toolbar and custom key registry (try F1 and Ctrl-D)')
    print(get_input(convertor=IntConvertor(), validators=[zero_to_ten_validator, not_5_validator],
                    prompt='',
                    convertor_error_fmt=convertor_fmt, validator_error_fmt=validator_fmt,
                    use_prompt_toolkit=True, key_registry=registry, use_bottom_toolbar=True, bottom_toolbar_str='Enter a non-zero integer between 0 and 10, but not 5'))
