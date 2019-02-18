"""
This file contains validator classes for cooked_input

For more validators: look at using validus:
    https://shopnilsazal.github.io/validus/readme.html

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

from __future__ import print_function

import os
import sys
import string
import re
import collections
from abc import ABCMeta, abstractmethod


from .error_callbacks import print_error, silent_error, DEFAULT_VALIDATOR_ERROR
from .input_utils import put_in_a_list, isstring


def in_any(value, validators, error_callback, validator_fmt_str):
    """
    return **True** if the value passes any of the ``validators`` - OR's the list of supplied `validators <validators.html>`_.

    :param Any value: the input value to validate
    :param List[Validator] validators: an iterable (list or tuple) containing the `validators <validators.html>`_ to use.
    :param Callable error_callback: a function called when an error occurs during validation
    :param str validator_fmt_str: format string for validation errors

    :return: boolean **True** if any of the validators pass, **False** if they all fail.
    """

    if validators is None:
        result = True
    elif isinstance(validators, collections.Iterable):  # list of validators (or other iterable)
        for validator in validators:
            if callable(validator):
                result = validator(value, error_callback, validator_fmt_str)
            else:  # validator is a value, not a function
                result = value == validator
            if result:
                break
    elif callable(validators):  # single validator function
        result = validators(value, error_callback, validator_fmt_str)
    else:   # single value
        result = value == validators

    return result


def in_all(value, validators, error_callback, validator_fmt_str):
    """
    return **True** if the value passes all of the validators - AND's the list of supplied `validators <validators.html>`_.

    :param Any value: the input value to validate
    :param List[Validator] validators: an iterable (list or tuple) containing the `validators <validators.html>`_ to use.
    :param Callable error_callback: a function called when an error occurs during validation
    :param str validator_fmt_str: format string to pass to the error callback routine for formatting the error.

    :return: boolean **True** if all of the validators pass, **False** if they all fail.
    """

    if validators is None:
        result = True
    elif isinstance(validators, collections.Iterable):
        result = all(validator(value, error_callback, validator_fmt_str) for validator in validators)
    elif callable(validators):
        result = validators(value, error_callback, validator_fmt_str)
    else:
        result = value == validators

    return result


def not_in(value, validators, error_callback, validator_fmt_str):
    """
    return **True** if the value does not pass any of the validators - NOT's the list of supplied `validators <validators.html>`_.

    :param Any value: the input value to validate
    :param List[Validator] validators: an iterable (list or tuple) containing the `validators <validators.html>`_ to use.
    :param allable error_callback: a function called when an error occurs during validation
    :param str validator_fmt_str: format string to pass to the error callback routine for formatting the error.

    :return: boolean **True** if none of the validators pass, **False** if they any of them pass.
    """
    result = False

    if validators is None:
        result = True
    elif isinstance(validators, collections.Iterable):  # list of validators (or other iterable)
        for validator in validators:
            if callable(validator):
                result = validator(value, silent_error, validator_fmt_str)
            else:   # validator is a value, not a function
                result = value == validator
            if result:
                break
    elif callable(validators):  # single validator function
        result = validators(value, silent_error, validator_fmt_str)
    else:   # single value
        result = value == validators

    if not result:
        return True
    else:
        error_callback(validator_fmt_str, value, 'value cannot match {}'.format(value))
        return False


def validate(value, validators, error_callback=print_error, validator_fmt_str=DEFAULT_VALIDATOR_ERROR):
    """
    return **True** is a value passes validation.

    :param Any value: the value to validate
    :param List[Validator] validators: an iterable (list or tuple) of `validators <validators.html>`_ to run on ``value``
    :param Callable error_callback: a function called when an error occurs during validation
    :param str validator_fmt_str: format string to pass to the error callback routine for formatting the error

    :return: **True** if the input passed validation, else **False**
    :rtype: boolean
    """
    result = None

    if callable(validators):
        result = validators(value, error_callback, validator_fmt_str)
    else:
        for v in validators:
            result = v(value, error_callback, validator_fmt_str)
            if not result:
                break

    return result


####
#### Validators:
####
class Validator(object):
    # Abstract base class for validation classes
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __call__(self, value, error_callback, validator_fmt_str):
        pass


class LengthValidator(Validator):
    """
    check the length of a value is in a range (open interval). For exact length match set ``min_len`` and ``max_len`` lengths
    to the same value.

    :param int min_len: the minimum required length for the input. If **None** (default), no minimum length is checked.
    :param int max_len: the maximum required length for the input. If **None** (default), no maximum length is checked.

    :return: **True** if the input passed validation
    :rtype: boolean

    Example::

        lv = LengthValidator(min_len=3, max_len=5)
        result = get_string(prompt="Enter a 3 to 5 char string", validators=lv)

    """
    def __init__(self, min_len=None, max_len=None):
        self._min_len = min_len
        self._max_len = max_len

    def __call__(self, value, error_callback, validator_fmt_str):
        try:
            val_len = len(value)
        except (TypeError):
            print('LengthValidator: value "{}" does not support __len__.'.format(value), file=sys.stderr)
            return False

        min_condition = (self._min_len is None or val_len >= self._min_len)
        max_condition = (self._max_len is None or val_len <= self._max_len)

        if min_condition and max_condition:
            return True
        elif not min_condition:
            error_callback(validator_fmt_str, value, 'too short (min_len={})'.format(self._min_len))
            return False
        else:
            error_callback(validator_fmt_str, value, 'too long (max_len={})'.format(self._max_len))
            return False

    def __repr__(self):
        return 'LengthValidator(min_len=%s, max_len=%s)' % (self._min_len, self._max_len)


class EqualToValidator(Validator):
    """
    check if a value is equal to a specified value.

    :param Any value: the value to match

    :return: **True** if the input passed validation, else **False**
    :rtype: boolean
    """
    def __init__(self, value):
        self._value = value

    def __call__(self, value, error_callback, validator_fmt_str):
        condition1 = (self._value is None or value == self._value)

        if condition1:
            return True
        else:
            error_callback(validator_fmt_str, value, 'value not equal to {}'.format(self._value))
            return False

    def __repr__(self):
        return 'EqualToValidator(value=%s)' % self._value


class RangeValidator(Validator):
    """
    check if a value is in a specified range (open interval.) The value can be of any type as long
    as the ``__ge__`` and ``__le__`` comparison functions are defined.

    :param Any min_val: The minimum allowed value (i.e. ``value`` must be >= ``min_val``). If **None** (the default), no minimum value is checked.
    :param Any max_val: The maximum allowed value (i.e. ``value`` must be <= max_val). If **None** (the default), no maximum value is checked.

    :return: **True** if the input passed validation, else **False**
    :rtype: boolean

    Example::

        rv = RangeValidator(min_val=1), max_val=10)
        result = get_int(prompt="Enter a number (1 to 10)", validators=rv)

    """
    def __init__(self, min_val=None, max_val=None):
        self._min_val = min_val
        self._max_val = max_val

    def __call__(self, value, error_callback, validator_fmt_str):
        try:
            min_condition = (self._min_val is None or value >= self._min_val)
        except (TypeError):
            print('RangeValidator: value "{}" does not support __ge__.'.format(value), file=sys.stderr)
            return False

        try:
            max_condition = (self._max_val is None or value <= self._max_val)
        except (TypeError):
            print('RangeValidator: value "{}" does not support __ge__.'.format(value), file=sys.stderr)
            return False

        if min_condition and max_condition:
            return True
        elif not min_condition:
            error_callback(validator_fmt_str, value, 'too low (min_val={})'.format(self._min_val))
            return False
        else:
            error_callback(validator_fmt_str, value, 'too high (max_val={})'.format(self._max_val))
            return False

    def __repr__(self):
        return 'RangeValidator(min_val=%s, max_val=%s)' % (self._min_val, self._max_val)


class ChoiceValidator(Validator):
    """
    check if a value is in a set of choices.

    :param Iterable choices: an iterable (tuple, list, or set) containing the allowed set of choices for the value.

    :return: **True** if the input passed validation, else **False**
    :rtype: boolean


    Example::

        colors = ["red", "green", "blue"]
        cv = ChoiceValidator(colors]
        result = get_string(prompt="Enter a color", validators=cv)

    """
    def __init__(self, choices):
        # note: if choices is mutable, the choices can change after instantiation
        self._choices = put_in_a_list(choices)

    def __call__(self, value, error_callback, validator_fmt_str):
        result = value in self._choices

        if result:
            return True
        else:
            choice_strs = [str(c) for c in self._choices]
            error_callback(validator_fmt_str, value, 'value must be one of: {}'.format(', '.join(choice_strs)))
            return False

    def __repr__(self):
        return 'ChoiceValidator(choices={})'.format(self._choices)


class NoneOfValidator(Validator):
    """
    check if a value does not pass validation for a list of `validators <validators.html>`_ (NOT operation).

    :param List[Validator] validators: a list of `validators <validators.html>`_ that should not pass
        validation on the input value

    :return: **True** if the input passed validation, else **False**
    :rtype: boolean

    .. note::
        if ``choices`` is mutable, it can be changed after the instance is created.

    Example::

        rv1 = RangeValidator(min_val=1, max_val=3)
        rv2 = EqualToValidator(7)
        nv = NoneOfValidator([rv1, rv2])
        prompt_str = "Enter a number (not between 1 and 3, and not 7)"
        result = get_int(prompt=prompt_str, validators = nv)

    """
    def __init__(self, validators):
        self._validators = validators

    def __call__(self, value, error_callback, validator_fmt_str):
        result = not_in(value, self._validators, error_callback, validator_fmt_str)

        # error callback handled within not_in call
        return result

    def __repr__(self):
        return 'NoneOfValidator(validators={})'.format(self._validators)


class AnyOfValidator(Validator):
    """
    check if a value matches any of a set of `validators <validators.html>`_ (OR operation).

    :param List[Validator] validators: a list of `validators <validators.html>`_. Returns **True**
        once any of the `validators <validators.html>`_ passes.

    :return: **True** if the input passed validation, else **False**
    :rtype: boolean

    .. note::
        if ``choices`` is mutable, it can be changed after the instance is created.

    Example::

        rv1 = RangeValidator(min_val=1, max_val=3)
        rv2 = EqualToValidator(7)
        nv = AnyOfValidator([rv1, rv2])
        prompt_str = "Enter a number (between 1 and 3, or 7)"
        result = get_int(prompt=prompt_str, validators = nv)

    """
    def __init__(self, validators):
        self._validators = validators

    def __call__(self, value, error_callback, validator_fmt_str):
        result = in_any(value, self._validators, error_callback, validator_fmt_str)
        return result

    def __repr__(self):
        return 'AnyOfValidator(validators={})'.format(self._validators)


class IsFileValidator(Validator):
    """
    check is a string is the name of an existing filename

    :param str value: the filename to verify

    :return: **True** if the input passed validation, else **False**
    :rtype: boolean
    """
    def __init__(self):
        pass

    def __call__(self, value, error_callback, validator_fmt_str):
        if os.path.isfile(value):
            return True
        else:
            error_callback(validator_fmt_str, value, '{} is not a valid file'.format(value))
            return False

    def __repr__(self):
        return 'IsFileValidator()'


class SimpleValidator(Validator):
    """
    use a simple function as a `validator <validators.html>`_. ``validator_func`` is any callable that takes a single
    value as input and returns **True** if the value passes (and **False** otherwise.) Used to wrap functions (e.g.
    `validus <https://shopnilsazal.github.io/validus/>`_ functions. Can also be used with `func.partial
    <https://docs.python.org/3/library/functools.html#partial-objects>`_ to wrap validation functions that take more complex parameters.

    :param Callable validator_func: a function (or other callable) called to validate the value
    :param str name: an optional string to use for the validator name in error messages

    :return: **True** if the input passed validation, else **False**
    :rtype: boolean

    Example::

        def is_even(value):
            return True if (value % 2) == 0 else False

        sv = SimpleValidator(is_even, "EvenNumberValidator")
        result = get_int(prompt="Enter an even number", validators = sv)
    """
    def __init__(self, validator_func, name='SimpleValidator value'):
        self._validator = validator_func
        self._name = None

    def __call__(self, value, error_callback, validator_fmt_str):
        result = self._validator(value)

        if not result:
            error_callback(validator_fmt_str, value, 'is not a valid {}'.format(self._name))

        return result

    def __repr__(self):
        return 'SimpleValidator(validators={})'.format(self._validator)


class RegexValidator(Validator):
    """
    check if a value matches a `regular expression <https://docs.python.org/3/library/re.html?highlight=re#module-re>`_.

    :param str pattern: the `regular expression <https://docs.python.org/3/library/re.html?highlight=re#module-re>`_ to match
    :param str regex_desc: a human readable string to use for the regular expression (used for error messages)

    :return: **True** if the input passed validation, else **False**
    :rtype: boolean

    Example::

        rv = RegexValidator(pattern=r'^[2-9]\d{9}$', regex_desc='phone number')
        result = get_string(prompt="Enter a phone number", validators = rv)

    """
    def __init__(self, pattern, regex_desc=None):
        self._regex = pattern
        self._regex_desc = regex_desc

    def __call__(self, value, error_callback, validator_fmt_str):
        try:
            result = re.search(self._regex, value)
        except (TypeError):
            print('RegexValidator: expected string or bytes-like object. "{}" not compatible.'.format(value), file=sys.stderr)
            return False

        if result:
            return True
        else:
            if self._regex == self._regex_desc:
                error_callback(validator_fmt_str, value, 'does not match pattern: {}'.format(self._regex_desc))
            else:
                error_callback(validator_fmt_str, value, 'is not a valid {}'.format(self._regex_desc))
            return False

    def __repr__(self):
        return 'RegexValidator(regex={})'.format(self._regex)


class PasswordValidator(Validator):
    """
    validate a password string.

    :param int min_len: the minimum allowed password length (default=1)
    :param int max_len: the maximum password length (default=64)
    :param int min_lower: the minimum number of lower case letters (default=``None``)
    :param int min_upper: the minimum number of upper case letters (default=``None``)
    :param int min_digits: the minimum number of digits (default=``None``)
    :param int min_puncts: the minimum number of punctuation characters (default=``None`)
    :param str allowed: a string containing the allowed characters in the password. Default is upper and lower case ascii
        letters, plus digits, plus punctuation characters
    :param str disallowed: a string containing characters not allowed in the password (default=``None``)

    :return: **True** if the input passed validation, else **False**
    :rtype: boolean

    Example::

        pv = PasswordValidator(min_len=5, min_lower=2, min_upper=2, min_digits=1, min_puncts=1)
        result = ci.get_string(prompt="Enter a password", validators=pv, hidden=True)

    """
    def __init__(self, min_len=None, max_len=None, min_lower=0, min_upper=0, min_digits=0, min_puncts=0,
                 allowed=None, disallowed=None):
        self._valid_chars = set(string.ascii_letters + string.digits + string.punctuation)
        self._min_len = min_len
        self._max_len = max_len
        self._min_lower = min_lower
        self._min_upper = min_upper
        self._min_digits = min_digits
        self._min_puncts = min_puncts

        if disallowed is not None:
            self._disallowed = set(disallowed)
        else:
            self._disallowed = set()

        if allowed is not None:
            self._valid_chars = set(allowed)

        self._valid_chars -= self._disallowed

    def __call__(self, value, error_callback, validator_fmt_str):
        if isstring(value) is False:
            print('PasswordValidator: value "{}" is not a string.'.format(value), file=sys.stderr)
            return False

        if len(set(value) - self._valid_chars):
            error_callback(validator_fmt_str, 'password', 'cannot contain any of the following characters: {}'.format(
                               set(value) - self._valid_chars))
            return False

        if self._min_len is not None and (len(value)) < self._min_len:
            error_callback(validator_fmt_str, 'password',
                           'too short (minimum length is {})'.format(self._min_len))
            return False

        if self._max_len and len(value) > self._max_len:
            error_callback(validator_fmt_str, 'password', 'too long (maximum length is {})'.format(self._max_len))
            return False

        if self._min_lower and len([c for c in value if c in string.ascii_lowercase]) < self._min_lower:
            error_callback(validator_fmt_str, 'password',
                           'too few lower case characters (minimum is {})'.format(self._min_lower))
            return False

        if self._min_upper and len([c for c in value if c in string.ascii_uppercase]) < self._min_upper:
            error_callback(validator_fmt_str, 'password', 'too few upper case characters (minimum is {})'.format(self._min_upper))
            return False

        if self._min_digits and len([c for c in value if c in string.digits]) < self._min_digits:
            error_callback(validator_fmt_str, 'password', 'too few digit characters (minimum is {})'.format(self._min_digits))
            return False

        if self._min_puncts and len([c for c in value if c in string.punctuation]) < self._min_puncts:
            error_callback(validator_fmt_str, 'password', 'too few punctuation characters (minimum is {})'.format(self._min_puncts,
                                                                                                                  set(string.punctuation) - self._disallowed))
            return False

        return True

    def __repr__(self):
        return 'PasswordValidator(allowed=%r, min_len=%r, max_len=%r, min_lowercase=%r, min_uppercase=%r, min_digits=%r, min_puncts=%r)' %\
               (self._valid_chars, self._min_len, self._max_len, self._min_lower, self._min_upper, self._min_digits, self._min_puncts)


class ListValidator(Validator):
    """
    Run a set of `validators <validators.html>`_ on a list.

    :param List[Validator] len_validators: a list of  `validators <validators.html>`_ to run on the length of the ``value``
        list. if **None** (default) no validation is done on the list length.
    :param List[Validator] elem_validators: a list of `validators <validators.html>`_ to apply to the
        elements of the list.
    :param str len_validator_fmt_str: a format string to use as an error message is the length of the ``value`` string
        does not pass the length validation (``len_validators``). If **None** (default), ``validator_fmt_str`` is used
        from the call to the validator.

    :return: **True** if the input passed validation, else **False**
    :rtype: boolean

    .. note::

        ``len_validators`` is usually an instance of :class:`EqualToValidator` for a list of a specific length, or
        :class:`RangeValidator` for a list whose length is in a range. :class:`LengthValidator` is not used as the ``value``
        passed to the validator is the length of the list, not the list itself.

    Example::

        colors = ['red', 'green', 'blue']
        len_validator = ci.RangeValidator(min_val=2, max_val=4)
        lvfs="List length {error_content} ({value})"
        elem_validator = ci.ChoiceValidator(colors)
        prompt_str = "Enter a list of 2 to 4 colors"
        lv = ci.ListValidator(len_validators=len_validator, elem_validators=elem_validator, len_validator_fmt_str=lvfs)
        result = ci.get_list(prompt=prompt_str, validators=lv)

    """
    def __init__(self, len_validators=None, elem_validators=None, len_validator_fmt_str=None):
        self._len_validators = len_validators
        self._elem_validators = elem_validators
        self._len_validator_fmt_str = len_validator_fmt_str

    def __call__(self, value, error_callback, validator_fmt_str):
        if self._len_validators:
            if self._len_validator_fmt_str is None:
                use_llvfs = validator_fmt_str
            else:
                use_llvfs = self._len_validator_fmt_str

            result = validate(len(value), self._len_validators, error_callback, use_llvfs)

            if not result:
                # error callback performed in len_validator
                return False

        if self._elem_validators:
            for item in value:
                result = validate(item, self._elem_validators, error_callback, validator_fmt_str)
                if not result:
                    # error callback performed in validate
                    return False

        return True

    def __repr__(self):
        return 'ListValidator()'.format()
