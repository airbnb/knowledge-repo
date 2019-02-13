
"""
Cooked input error callbacks

see: https://github.com/lwanger/cooked_input for more information.

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

from __future__ import print_function

import sys
import logging

### cooked input custom exceptions
class MaxRetriesError(RuntimeError):
    """
    raised when the maximum number of retries is exceeded.
    """
    pass

class ValidationError(ValueError):
    """
    raised when a value does not pass validation.
    """
    pass

class ConvertorError(ValueError):
    """
    raised by a when a value does not pass conversion.
    """
    pass

### Default error callback format strings
DEFAULT_CONVERTOR_ERROR = '"{value}" cannot be converted to {error_content}'
DEFAULT_VALIDATOR_ERROR = '"{value}" {error_content}'

### error callback routines

def print_error(fmt_str, value, error_content):
    """
    send errors to stdout. This displays errors on the screen.

    :param int fmt_str: a Python `format string <https://docs.python.org/3/library/string.html#formatspec>`_
      for the error. Can use arguments **{value}** and **{error_content}** in the format string
    :param Any value: the value the caused the error
    :param str error_content: additional information for the error

    :return: None
    """
    print(fmt_str.format(value=value, error_content=error_content), file=sys.stderr)


def silent_error(fmt_str, value, error_content):
    """
        Ignores errors, causing them to be silent.

        :param str fmt_str: a Python `format string <https://docs.python.org/3/library/string.html#formatspec>`_
          for the error. Can use arguments **{value}** and **{error_content}** in the format string
        :param Any value: the value the caused the error
        :param str error_content: additional information for the error

        :return: None
    """
    pass


def log_error(fmt_str, value, error_content):
    """
        send errors to the log. See logging for details on using logs.

        :param str fmt_str: a Python `format string <https://docs.python.org/3/library/string.html#formatspec>`_
          for the error. Can use arguments **{value}** and **{error_content}** in the format string
        :param Any value: the value the caused the error.
        :param str error_content: additional information for the error

        :return: None
    """
    logging.error(fmt_str.format(value=value, error_content=error_content))
