"""
This file contains cleaner classes for cooked_input

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

import re
from string import capwords
from abc import ABCMeta, abstractmethod

from .input_utils import put_in_a_list, cap_last_word

LOWER_CAP_STYLE = 1
UPPER_CAP_STYLE = 2
FIRST_WORD_CAP_STYLE = 3
LAST_WORD_CAP_STYLE = 4
ALL_WORDS_CAP_STYLE = 5

CAP_STYLES = { LOWER_CAP_STYLE, UPPER_CAP_STYLE, FIRST_WORD_CAP_STYLE, LAST_WORD_CAP_STYLE, ALL_WORDS_CAP_STYLE }

CAP_STYLE_STRS = {
    'lower': LOWER_CAP_STYLE,
    'upper': UPPER_CAP_STYLE,
    'first_word': FIRST_WORD_CAP_STYLE,
    'capitalize': FIRST_WORD_CAP_STYLE,
    'last_word': LAST_WORD_CAP_STYLE,
    'all_words': ALL_WORDS_CAP_STYLE,
    'capwords': ALL_WORDS_CAP_STYLE
}


###
### Cleaners:
###
class Cleaner(object):
    # Abstract base class for cleaner classes
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __call__(self, value):
        pass


class CapitalizationCleaner(Cleaner):
    """
    :param CAP_STYLE_STR style: (optional) capitalization style to use. Defaults to  ``LOWER_CAP_STYLE``

    :return: the cleaned (capitalized) value
    :rtype: str

    Capitalize the value using the specified style

    The styles are equivalent to the following:

    +---------------------------+--------------------------------+
    | **style**                 | **equivalent string function** |
    +---------------------------+--------------------------------+
    | ``LOWER_CAP_STYLE``       | lower                          |
    +---------------------------+--------------------------------+
    | ``UPPER_CAP_STYLE``       | upper                          |
    +---------------------------+--------------------------------+
    | ``FIRST_WORD_CAP_STYLE``  | capitalize                     |
    +---------------------------+--------------------------------+
    | ``LAST_WORD_CAP_STYLE``   | --  [#f1]_                     |
    +---------------------------+--------------------------------+
    | ``ALL_WORDS_CAP_STYLE``   | capwords                       |
    +---------------------------+--------------------------------+

.. [#f1] There is no standard library function for capitalizing the last word in a string. This was added to properly 
  capitalize family names, (e.g. `"van Rossum"`.) This parameter is dedicated to Colleen, who will be happy to capitalize
  on getting the last word.

    """
    def __init__(self, style='lower'):
        if isinstance(style, int):
            if style in CAP_STYLES:
                self._style = style
            else:
                raise ValueError('CapitalizationCleaner: {} is not a valid capitalization style'.format(style))
        else:   # a string type
            if style in CAP_STYLE_STRS:
                self._style = CAP_STYLE_STRS[style]
            else:
                raise ValueError('CapitalizationCleaner: {} is not a valid capitalization style'.format(style))

    def __call__(self, value):
        if self._style == LOWER_CAP_STYLE:
            return value.lower()
        elif self._style == UPPER_CAP_STYLE:
            return value.upper()
        elif self._style == FIRST_WORD_CAP_STYLE:
            return value.capitalize()
        elif self._style == LAST_WORD_CAP_STYLE:
            return cap_last_word(value)
        else:    # ALL_WORDS_CAP_STYLE:
            return capwords(value)

    def __repr__(self):
        return 'CapitalizationCleaner(style={})'.format(self._style)


class StripCleaner(Cleaner):
    """
    :param bool lstrip: (optional) strips white space from the left side of the value if **True** (default)
    :param bool rstrip: (optional) strips white space from the right side of the value if **True** (default)

    :return: the cleaned (stripped) value
    :rtype: str

    Strips white space from the input value. Strips from the left side if lstrip=True, and from the
    right side if rstrip=True. Both are True by default (i.e. strips from both left and right).
    """
    def __init__(self, lstrip=True, rstrip=True):
        self._lstrip = lstrip
        self._rstrip = rstrip

    def __call__(self, value):
        result = value
        if self._lstrip:
            result = result.lstrip()
        if self._rstrip:
            result = result.rstrip()
        return result

    def __repr__(self):
        return 'StripCleaner(lstrip=%r, rstrip=%s)' % (self._lstrip, self._rstrip)


class ChoiceCleaner(Cleaner):
    """
    :param List[str] choices: the list of choices to match
    :param bool case_sensitive: (optional) if **True** (default) matching the choice is case sensitive, 
      otherwise matching is case insensitive

    :return: the cleaned (matched choice from the ``choices`` list) value or the original value if no match is found
    :rtype: str (type is dependent on the mapped value in ``choices`` but is generally `str`)

    .. note:: The cleaned output uses the same capitalization as the item matched from the choices list regardless of the
        ``case_sensitive`` parameter.

    ChoiceCleaner tries to replace the input value with a single element from a list of choices by finding the unique
    element starting with the input value. If no single element can be identified, the input value is returned (i.e. no
    cleaning is performed.) This is a complicated way of saying you can type in the first few letters of an input and
    the cleaner will return the choice that starts with those letters if it can determined which one it is.

    For example::

        ChoiceCleaner(choices=['blue', 'brown', 'green'], case_sensitive=True)

    will with the following input values would return the following values:

        +-------+---------+--------------------------------------------------------------------+
        | value | returns | note                                                               |
        +=======+=========+====================================================================+
        | 'g'   | 'green' |                                                                    |
        +-------+---------+--------------------------------------------------------------------+
        | 'br'  | 'brown' |                                                                    |
        +-------+---------+--------------------------------------------------------------------+
        | 'blu' | 'blue'  |                                                                    |
        +-------+---------+--------------------------------------------------------------------+
        | 'b'   | 'b'     | original value returned as can't tell between 'brown' and 'blue'   |
        +-------+---------+--------------------------------------------------------------------+
        | 'BR'  | 'BR'    | original value returned as case of the input does not match [#f2]_ |
        +-------+---------+--------------------------------------------------------------------+

.. [#f2] Would return `"brown"` if ``case_sensitive`` is **False**
    """
    def __init__(self, choices, case_sensitive=True):
        self._case_sensitive = case_sensitive

        # create a dictionary as choices may not be strings
        if case_sensitive:
            self._str_choices = {str(choice): choice for choice in choices}
        else:
            self._str_choices = {str(choice).lower(): choice for choice in choices}

    def __call__(self, value):
        if self._case_sensitive:
            str_value = str(value)
        else:
            str_value = str(value).lower()
        matches = [v for k, v in self._str_choices.items() if k.startswith(str_value)]

        if len(matches) == 1:
            return matches[0]
        elif value in self._str_choices:  # one value is an exact subset of another
            return self._str_choices[value]
        else:
            return value

    def __repr__(self):
        return 'ChoiceCleaner(choices={})'.format(self._str_choices)


class RemoveCleaner(Cleaner):
    """
    :param List[str] patterns: a list of strings to remove
    :param int count: (optional) the maximum number of substitutions to perform on the input value. Default
      is to remove all occurences

    :return: the cleaned (``patterns`` removed) value
    :rtype: str

    Removes all occurrences of any of the strings in the ``patterns`` list from the input value.
    """
    def __init__(self, patterns, count=0):
        self._patterns = put_in_a_list(patterns)
        self._count = count

    def __call__(self, value):
        result = value
        for pattern in self._patterns:
            if self._count == 0:
                result = result.replace(pattern, '')
            else:
                result = result.replace(pattern, '', self._count)

        return result

    def __repr__(self):
        return 'ReplaceCleaner(patterns={})'.format(self._patterns)


class ReplaceCleaner(Cleaner):
    """
    :param str old: string to replace
    :param str new: string to substitute for occurrences of ``old``
    :param int count: (optional) the maximum number of substitutions to perform on the input value. Default
      is to replace all occurences

    :return: the cleaned (``old`` replaced with ``new``) value
    :rtype: str

    Replaces occurrences of ``old`` string with ``new`` string from the input value. If `count` is specified the first
    ``count`` occurences, from left to right, are replaced. If count is **0**, or not speciffied, all occurences are replaced.
    """
    def __init__(self, old, new, count=0):
        self._old = str(old)
        self._new = str(new)
        self._count = count

    def __call__(self, value):
        if self._count == 0:
            result = value.replace(self._old, self._new)
        else:
            result = value.replace(self._old, self._new, self._count)

        return result

    def __repr__(self):
        return 'ReplaceCleaner(old="{}", new="{}")'.format(self._old, self._new)


class RegexCleaner(Cleaner):
    """
    :param Pattern[str] pattern: regular expression to search for
    :param str repl: string to substitute for occurences of ``pattern``
    :param int count: (optional) the maximum number of substitutions to perform on the input value. Default is to replace
      all occurences
    :param flags: (optional) flags. Default is no flags. See below for details
    
    :return: the cleaned (**pattern** replaced with **repl**) value
    :rtype: str

    Return the string obtained by replacing the leftmost non-overlapping occurrences of `pattern` in the input value
    by the replacement `repl`. If the pattern isn’t found in the input value, the value is returned unchanged.
    ``Count`` occurences, from left to right, are replaced. If count is **0**, or not speciffied, all occurences are replaced.

    For more information on regular expressions and the meaning of count and flags. See the 
    `re.sub <https://docs.python.org/3/library/re.html#re.sub>`_ function in the `re <https://docs.python.org/3/library/re.html>`_
    module in the Python standard library.
    """
    def __init__(self, pattern, repl, count=0, flags=0):
        self._pattern = pattern
        self._repl = repl
        self._count = count
        self._flags = flags

    def __call__(self, value):
        result = re.sub(self._pattern, self._repl, value, self._count, self._flags)
        return result

    def __repr__(self):
        return 'RegexCleaner(pattern={}, repl={}, count={}, flags={})'.format(self._pattern, self._repl, self._count, self._flags)
