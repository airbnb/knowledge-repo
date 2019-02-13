"""
get_input module to get values from the command line.

see: https://github.com/lwanger/cooked_input for more information.

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

from __future__ import unicode_literals

import sys
import collections
import logging
import getpass

from .error_callbacks import MaxRetriesError, ValidationError, ConvertorError
from .error_callbacks import print_error, DEFAULT_CONVERTOR_ERROR, DEFAULT_VALIDATOR_ERROR
from .validators import Validator, RangeValidator, in_all, LengthValidator
from .convertors import IntConvertor, FloatConvertor, BooleanConvertor, DateConvertor
from .convertors import YesNoConvertor, ListConvertor
from .cleaners import StripCleaner
from .input_utils import compose, isstring


# Custom exceptions for get_input
class GetInputInterrupt(KeyboardInterrupt):
    """
    A cancellation command (COMMAND_ACTION_CANCEL) occurred.
    """
    pass


class RefreshScreenInterrupt(Exception):
    """
    When raised, directs ``cooked_input`` to refresh the display. Used primarily to refresh table items.
    """
    pass


class PageUpRequest(Exception):
    """
    When raised, directs ``cooked_input`` to go to the previous page in paginated tables
    """
    pass


class PageDownRequest(Exception):
    """
    When raised, directs ``cooked_input`` to go to the next page in paginated tables
    """
    pass


class FirstPageRequest(Exception):
    """
    When raised, directs ``cooked_input`` to go to the first page in paginated tables
    """
    pass


class LastPageRequest(Exception):
    """
    When raised, directs ``cooked_input`` to go to the last page in paginated tables
    """
    pass


class UpOneRowRequest(Exception):
    """
    When raised, directs ``cooked_input`` to scroll up one row in paginated tables
    """
    pass


class DownOneRowRequest(Exception):
    """
    When raised, directs ``cooked_input`` to scroll down one row in paginated tables
    """
    pass


# Python 2/3 compatibility
if sys.version_info[0] > 2:  # For Python 3
    def raw_input(prompt_msg):
        return input(prompt_msg)


# Named tuple and action types for GetInput commands
CommandResponse = collections.namedtuple('CommandResponse', 'action value')

# Command action constants
COMMAND_ACTION_USE_VALUE = 'enter_value_action'
COMMAND_ACTION_CANCEL = 'cancel_input_action'
COMMAND_ACTION_NOP = 'nop_action'

COMMAND_ACTIONS = {
    COMMAND_ACTION_USE_VALUE: 'enter_value_action',
    COMMAND_ACTION_CANCEL: 'cancel_input_action',
    COMMAND_ACTION_NOP: 'nop_action',
}


class GetInputCommand(object):
    """
    `GetInputCommand` is used to create commands that can be used while getting input from :meth:`GetInput.get_input`

    :param Callable[str, str, Dict[str, Any], Tuple[str, Any]] cmd_action: callback function used to process the command
    :param Dict[Any, Any] cmd_dict: (optional) a dictionary of data passed to the ``cmd_action`` callback function

    Each command has a callback function (``cmd_action``) and optional data (``cmd_dict``).

    ``cmd_action`` is a callback function used for the command. The callback is called as follows

        .. py:function:: cmd_action(cmd_str, cmd_vars, cmd_dict)

          :param str cmd_str: the string used to call the command
          :param str cmd_vars: additional arguments for the command (i.e. the rest of string used for the command input)
          :param Dict[str, Any] cmd_dict: a dictionary of additional data for processing the command (often **None**)

    Command callback functions return a a tuple containing (`COMMAND_ACTION_TYPE`, value), where the command action
    type is one of the following:

    +-------------------------------+--------------------------------------------------------------------------+
    | **Action**                    |    **Result**                                                            |
    +===============================+==========================================================================+
    | ``COMMAND_ACTION_USE_VALUE``  |  use the second value of the tuple as the input                          |
    +-------------------------------+--------------------------------------------------------------------------+
    | ``COMMAND_ACTION_CANCEL``     |  cancel the current input (raises :class:`GetInputInterrupt` exception)  |
    +-------------------------------+--------------------------------------------------------------------------+
    | ``COMMAND_ACTION_NOP``        |  do nothing - continues to ask for the input                             |
    +-------------------------------+--------------------------------------------------------------------------+

    For convenience command action callbacks can return a :class:`CommandResponse` namedtuple instance::

         CommandResponse(action, value)

    The ``cmd_dict`` dictionary can be used to pass data useful in processing the command. For instance, a database
    session and the name of the user can be passed with::

        cmd_dict = {'session': db_session, 'user_name': user_name }
        lookup_user_cmd = GetInputCommand(lookup_user_action, cmd_dict)

    The following show examples of of each type of command::

        def use_color_action(cmd_str, cmd_vars, cmd_dict):
            print('Use "red" as the input value')
            return (COMMAND_ACTION_USE_VALUE, 'red')

        def cancel_action(cmd_str, cmd_vars, cmd_dict):
            return CommandResponse(COMMAND_ACTION_CANCEL, None)

        def show_help_action(cmd_str, cmd_vars, cmd_dict):
            print('Commands:')
            print('---------')
            print('/?  - show this message')
            print('/cancel - cancel this operation')
            print('/red    - use red as a value')
            print('/reverse - return the user\'s name reversed')
            return CommandResponse(COMMAND_ACTION_NOP, None)

        cmds = { '/?': GetInputCommand(show_help_action),
                 '/cancel': GetInputCommand(cancel_action),
                 '/red': GetInputCommand(use_color_action, {'color': 'red'}),
                 '/reverse': GetInputCommand(user_color_action, {'user': 'fred'}) }

        try:
            result = get_string(prompt=prompt_str, commands=cmds)
        except GetInputInterrupt:
            print('Operation cancelled (received GetInputInterrupt)')

.. note::
    Nothing stops you from using ``cooked_input`` to get additional input within a command action callback. For example,
    the cancel command could be extended to confirm the user wants to cancel the current input::

        def cancel_action(cmd_str, cmd_vars, cmd_dict):
            response = get_yes_no(prompt="Are you sure you want to cancel?", default='no')

            if response == 'yes':
                print('operation cancelled!')
                return CommandResponse(COMMAND_ACTION_CANCEL, None)
            else:
                return CommandResponse(COMMAND_ACTION_NOP, None)
    """
    def __init__(self, cmd_action, cmd_dict=None):
        self.cmd_action = cmd_action
        self.cmd_dict = cmd_dict

    def __call__(self, cmd_str, cmd_vars):
        return self.cmd_action(cmd_str, cmd_vars, self.cmd_dict)

    def __repr__(self):
        return 'GetInputCommand(cmd_action={}, cmd_dict={})'.format(self.cmd_action, self.cmd_dict)


# Named tuple for return values of GetInput.process_value
ProcessValueResponse = collections.namedtuple('ProcessValueResponse', 'valid value')


class GetInput(object):
    """
    Class to get cleaned, converted, validated input from the command line. This is the central class used for
    cooked_input.

    :param List[Cleaner] cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value
    :param Convertor convertor: the `convertor <convertors.html>`_ to apply to the cleaned value
    :param List[Validator] validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param options: see below

    Options:

        **prompt**: the string to use for the prompt. For example prompt="Enter your name"

        **required**: **True** if a non-blank value is required, **False** if a blank response is OK.

        **default**: the default value to use if a blank string is entered. This takes precedence over required
            (i.e. a blank response will return the default value.)

        **default_str**: the string to use for the default value. In general just set the default option.

        **hidden**: the input typed should not be displayed. This is useful for entering passwords.

        **retries**: the maximum number of attempts to allow before raising a :class:`MaxRetriesError` exception.

        **error_callback**: a callback function to call when an error is encountered. Defaults to :func:`print_error`

        **convertor_error_fmt**: format string to use for `convertor <convertors.html>`_ errors. Defaults to
            **DEFAULT_CONVERTOR_ERROR**. Format string receives two variables - **{value}** the value that failed
            conversion, and **{error_content}** set by the convertor.

        **validator_error_fmt**: format string to use for `validator <validators.html>`_ errors. Defaults
            to **DEFAULT_VALIDATOR_ERROR**. Format string receives two variables - **{value}** the value that
            failed conversion, and **{error_content}** set by the validator.

        **commands**: an optional dictionary of commands. See below for more details.

    Commands:

        :class:`GetInput` optionally takes a dictionary containing commands that can be run from the input prompt. The key for
        each command is the string used to call the command and the value is an instance of the :class:`GetInputCommand` class
        for the command. For intance, the following dictionary sets two different command string (**/?** and **/help**)
        to call a function to show help information::

            {
                "/?": GetInputCommand(show_help_action)),
                "/help": GetInputCommand(show_help_action)),
            }

        For more information see :class:`GetInputCommand`
    """
    def __init__(self, cleaners=None, convertor=None, validators=None, **options):
        self.cleaners = cleaners
        self.convertor = convertor
        self.validators = validators

        self.prompt_str = ''
        self.required = True
        self.default_val = None
        self.default_string = None
        self.hidden = False
        self.max_retries = None
        self.error_callback = print_error
        self.convertor_error_fmt = DEFAULT_CONVERTOR_ERROR
        self.validator_error_fmt = DEFAULT_VALIDATOR_ERROR
        self.commands = {}

        for k, v in options.items():
            if k == 'prompt':
                self.prompt_str = '%s' % v
            elif k == 'required':
                self.required = True if v else False
            elif k == 'default':
                if v is None:
                    self.default_val = None
                else:
                    self.default_val = str(v)
            elif k == 'default_str':  # for get_from_table may want to display value but return id.
                self.default_string = v
            elif k == 'hidden':
                self.hidden = v
            elif k == 'retries':
                self.max_retries = v
            elif k == 'error_callback':
                self.error_callback = v
            elif k == 'convertor_error_fmt':
                self.convertor_error_fmt = v
            elif k == 'validator_error_fmt':
                self.validator_error_fmt = v
            elif k == 'commands':
                self.commands = v
            else:
                logging.warning('Warning: get_input received unknown option (%s)' % k)

        if self.default_val is not None:
            # TODO - have a way to set blank if there is a default_val... a command like 'blank' or 'erase'?
            # logging.warning('Warning: both required and a default value specified. Blank inputs will use default value.')
            self.required = True

        if not self.default_string:
            if not self.required and not self.default_val:
                self.default_string = ' (enter to leave blank)'
            elif self.default_val:
                self.default_string = ' (enter for: %s)' % self.default_val
            else:
                self.default_string = ''


    def get_input(self):
        """
        Get input from the command line and return a validated response.

        :return: the cleaned, converted, validated input
        :rtype: Any (dependent on the value returned from the :class:`convertors`)

        This method prompts the user for an input, and returns the cleaned, converted, and validated input.
        """
        retries = 0
        input_str = '{}{}: '.format(self.prompt_str, self.default_string)
        print('')

        while (self.max_retries is None) or (retries < self.max_retries):
            if self.hidden:
                response = getpass.getpass(prompt=input_str)
            else:
                response = raw_input(input_str)

            if self.commands:
                command_action = None
                for cmd in self.commands:
                    if response.lstrip().startswith(cmd):
                        idx = response.find(cmd)
                        cmd_str = response[:idx+len(cmd)].strip()
                        cmd_vars = response[idx+len(cmd):].strip()
                        command_action, command_value = self.commands[cmd](cmd_str, cmd_vars)
                        break

                if command_action:
                    if command_action == COMMAND_ACTION_USE_VALUE:
                        response = command_value
                    elif command_action == COMMAND_ACTION_NOP:
                        continue
                    elif command_action == COMMAND_ACTION_CANCEL:
                        raise GetInputInterrupt
                    else:
                        raise RuntimeError('GetInput.get_input: Unknown command action specified ({})'.format(command_action))

            if not self.required and not response:
                return None
            elif self.default_val and not response:
                valid_response, converted_response = self.process_value(self.default_val)

                if valid_response:
                    return converted_response
                else:
                    raise ValidationError('default value "{!r}" did not pass validation.'.format(self.default_val))
            elif response:
                valid_response, converted_response = self.process_value(response)

                if valid_response:
                    break
                else:
                    retries += 1
                    # TODO: show validation error messages
                    continue

        if valid_response:
            return converted_response
        else:
            raise MaxRetriesError('Maximum retries exceeded')


    def process_value(self, value):
        """
        :param str value: the value to process

        :return: Return a **ProcessValueResponse** namedtuple (valid, converted_value)
        :rtype: NamedTuple[bool, Any]

        Run a value through cleaning, conversion, and validation. This allows the same processing used
        in :meth:`GetInput.get_input` to be performed on a value. For instance, the same processing used for getting
        keyboard input can be applied to the value from a gui or web form input.

        The **ProcessValueResponse** namedtuple has elements **valid** and **value**. If the value was
        successfully cleaned, converted and validated, **valid** is True and **value** is the converted and cleaned
        value. If not, **valid** is **False**, and **value** is **None**.
        """
        if self.cleaners:
            cleaned_response = compose(value, self.cleaners)
        else:
            cleaned_response = value

        try:
            if self.convertor:
                converted_response = self.convertor(cleaned_response, self.error_callback, self.convertor_error_fmt)
            else:
                converted_response = cleaned_response
        except ConvertorError:
            return (False, None)

        valid_response = in_all(converted_response, self.validators, self.error_callback, self.validator_error_fmt)

        if valid_response:
            # return (True, converted_response)
            return ProcessValueResponse(True, converted_response)

        else:
            # return (False, None)
            return ProcessValueResponse(False, None)


#############################
### Convenience Functions ###
#############################

def get_input(cleaners=None, convertor=None, validators=None, **options):
    """
    :param List[Cleaner] cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value. Not needed in general.
    :param Convertor convertor: the `convertor <convertors.html>`_ to apply to the cleaned value
    :param List[Validator] validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param options: all :class:`GetInput` options supported, see :class:`GetInput` documentation for details.

    :return: the cleaned, converted, validated input string
    :rtype: Any (returned value is dependent on type returned from ``convertor``)

    Convenience function to create a :class:`GetInput` instance and call its `get_input` function. See
    :func:`GetInput.get_input` for more details.
    """
    gi = GetInput(cleaners, convertor, validators, **options)
    return gi.get_input()


def process_value(value, cleaners=None, convertor=None, validators=None, error_callback=print_error,
            convertor_error_fmt=DEFAULT_CONVERTOR_ERROR, validator_error_fmt=DEFAULT_VALIDATOR_ERROR):
    """
    :param str value: the value to process
    :param List[Cleaner] cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value
    :param Convertor convertor: the `convertor <convertors.html>`_ to apply to the cleaned value
    :param List[Validator] validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param str error_callback: a callback function to call when an error is encountered. Defaults to :func:`print_error`
    :param str convertor_error_fmt: format string to use for convertor errors. Defaults to **DEFAULT_CONVERTOR_ERROR**
    :param str validator_error_fmt: format string to use for validator errors. Defaults to **DEFAULT_VALIDATOR_ERROR**

    :return: the cleaned, converted validated input value.
    :rtype: Any (returned value is dependent on type returned from ``convertor``)

    Convenience function to create a :class:`GetInput` instance and call its process_value function. See
    :func:`GetInput.process_value` for more details. See  :class:`GetInput` for more information on the
    `error_callback`, `convertor_error_fmt`, and `validator_error_fmt` parameters.
    """
    options = {'error_callback': error_callback, 'convertor_error_fmt': convertor_error_fmt,
               'validator_error_fmt': validator_error_fmt}

    gi = GetInput(cleaners, convertor, validators, **options)
    return gi.process_value(value)


def get_string(cleaners=(StripCleaner()), validators=None, min_len=None, max_len=None, **options):
    """
    :param List[Cleaner] cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value.
    :param List[Validator] validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param int min_len: the minimum allowable length for the string. No minimum length if None (default)
    :param int max_len: the maximum allowable length for the string. No maximum length if None (default)
    :param options: all :class:`GetInput` options supported, see :class:`GetInput` documentation for details.

    :return: the cleaned, converted, validated string
    :rtype: str

    Convenience function to get a string value.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter some text'

    use_validators = []
    if min_len is not None or max_len is not None:
        use_validators.append(LengthValidator(min_len=min_len, max_len=max_len))

    if isinstance(validators, Validator):
        use_validators.append(validators)
    elif validators is not None:
        use_validators.extend(validators)

    result = GetInput(cleaners, None, use_validators, **new_options).get_input()
    return result


def get_int(cleaners=None, validators=None, minimum=None, maximum=None, base=10, **options):
    """
    :param List[Cleaner] cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value.
    :param List[Validator] validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param int minimum: minimum value allowed. Use None (default) for no minimum value.
    :param int maximum: maximum value allowed. Use None (default) for no maximum value.
    :param int base: Convert a string in radix base to an integer. Base defaults to 10.
    :param options: all :class:`GetInput` options supported, see :class:`GetInput` documentation for details.

    :return: the cleaned, converted, validated int value
    :rtype: int

    Convenience function to get an integer value. See the documentation for the Python
    `int <https://docs.python.org/3/library/functions.html#int>`_ builtin function for further description
    of the `base` parameter.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter a whole (integer) number'

    if minimum is None and maximum is None:
        val_list = validators
    else:
        irv = RangeValidator(min_val=minimum, max_val=maximum)
        if validators is None:
            val_list = irv
        elif callable(validators):
            val_list = [validators, irv]
        else:
            val_list = validators + [irv]

    result = GetInput(cleaners, IntConvertor(base=base), val_list, **new_options).get_input()
    return result


def get_float(cleaners=None, validators=None, minimum=None, maximum=None, **options):
    """
    :param List[Cleaner] cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value.
    :param List[Validator] validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param float minimum: minimum value allowed. Use None (default) for no minimum value.
    :param float maximum: maximum value allowed. Use None (default) for no maximum value.
    :param options: all :class:`GetInput` options supported, see :class:`GetInput` documentation for details.

    :return: the cleaned, converted, validated float value
    :rtype: float

    Convenience function to get an float value.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter an real (floating point) number'

    if minimum is None and maximum is None:
        val_list = validators
    else:
        irv = RangeValidator(min_val=minimum, max_val=maximum)
        if validators is None:
            val_list = irv
        elif callable(validators):
            val_list = [validators, irv]
        else:
            val_list = validators + [irv]

    result = GetInput(cleaners, FloatConvertor(), val_list, **new_options).get_input()
    return result


def get_boolean(cleaners=(StripCleaner()), validators=None, **options):
    """
    :param List[Cleaner] cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value.
    :param List[Validator] validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param options: all :class:`GetInput` options supported, see :class:`GetInput` documentation for details.

    :return: the cleaned, converted, validated boolean value
    :rtype: bool

    Convenience function to get a Boolean value. See :class:`BooleanConvertor` for a list of values accepted
    for `True` and `False`.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter true or false'

    result = GetInput(cleaners, BooleanConvertor(), validators, **new_options).get_input()
    return result


# def get_date(cleaners=(StripCleaner()), validators=None, **options):
def get_date(cleaners=(StripCleaner()), validators=None, minimum=None, maximum=None, **options):
    """
    :param List[Cleaner] cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value. Not needed in general.
    :param List[Validator] validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param datetime minimum: earliest date allowed. Use None (default) for no minimum value.
    :param datetime maximum: latest date allowed. Use None (default) for no maximum value.
    :param options: all :class:`GetInput` options supported, see :class:`GetInput` documentation for details.

    :return: the cleaned, converted, validated date value
    :rtype: `datetime <https://docs.python.org/3/library/datetime.html#datetime.datetime>`_

    Convenience function to get a date value. See :class:`DateConvertor` for more information on converting dates. Get_date
    can be used to get both times and dates.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter a date'

    if minimum is None and maximum is None:
        val_list = validators
    else:
        irv = RangeValidator(min_val=minimum, max_val=maximum)
        if validators is None:
            val_list = irv
        elif callable(validators):
            val_list = [validators, irv]
        else:
            val_list = validators + [irv]

    result = GetInput(cleaners, DateConvertor(), val_list, **new_options).get_input()
    # result = GetInput(cleaners, DateConvertor(), validators, **new_options).get_input()
    return result


def get_yes_no(cleaners=(StripCleaner()), validators=None, **options):
    """
    :param List[Cleaner] cleaners: list of `cleaners <cleaners.html>`_ to apply to clean the value. Not needed in general.
    :param List[Validator] validators: list of `validators <validators.html>`_ to apply to validate the cleaned and converted value
    :param options: all :class:`GetInput` options supported, see :class:`GetInput` documentation for details.

    :return: the cleaned, converted, validated yes/no value
    :rtype: str (**"yes"** or **"no"**)

    Convenience function to get an yes/no value. See :class:`YesNoConvertor` for a list of values accepted
    for `yes` and `no`.
    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter yes or no'

    result = GetInput(cleaners, YesNoConvertor(), validators, **new_options).get_input()
    return result


def get_list(elem_get_input=None, cleaners=None, validators=None, value_error_str='list of values', delimiter=',', **options):
    """
    :param GetInput elem_get_input: an instance of a :class:`GetInput` to apply to each element
    :param List[Cleaner] cleaners: cleaners to be applied to the input line before the :class:`ListConvertor` is applied.
    :param List[Validator] validators: list of `validators <validators.html>`_ to apply to validate the converted list
    :param str value_error_str: the error string for improper value inputs
    :param str delimiter: the delimiter to use between values
    :param options: all get_input options supported, see get_input documentation for details.

    :return: the cleaned, converted, validated list of values. For more information on the `value_error_str`,
      `delimeter`, `elem_convertor`, and elem_valudator` parameters see :class:`ListConvertor`.
    :rtype: List[Any]

    Get a homogenous list of values. The :meth:`GetInput.process_value` method on the ``elem_get_input`` :class:`GetInput`
    instance is called for each element in the list.

    Example usage - get a list of integers between 3 and 5 numbers long, separated by colons (:)::

        elem_gi = GetInput(convertor=IntConvertor())
        length_validator = RangeValidator(min_val=3, max_val=5)
        list_validator = ListValidator(len_validator=length_validator)
        prompt_str = 'Enter a list of integers, each between 3 and 5, separated by ":"'
        result = get_list(prompt=prompt_str, elem_get_input=elem_gi, validators=list_validator, delimiter=":")

    """
    new_options = dict(options)

    if 'prompt' not in options:
        new_options['prompt'] = 'Enter a list of values (separated by "{}")'.format(delimiter)

    error_callback = print_error
    validator_error_fmt = DEFAULT_VALIDATOR_ERROR

    for k, v in options.items():
        if k == 'error_callback':
            error_callback = v
        elif k == 'validator_error_fmt':
            validator_error_fmt = v
        elif k == 'default':
            if v is None:
                default_val = None
            else:
                if isstring(v):
                    default_val = v
                elif isinstance(v, collections.Iterable):
                    default_val = (delimiter + ' ').join(v)
                else:
                    default_val = str(v)
            new_options['default'] = default_val

    new_options['error_callback'] = error_callback
    new_options['validator_error_fmt'] = validator_error_fmt
    convertor = ListConvertor(value_error_str=value_error_str, delimiter=delimiter, elem_get_input=elem_get_input)
    gi = GetInput(cleaners, convertor, validators, **new_options)

    result = gi.get_input()
    return result
