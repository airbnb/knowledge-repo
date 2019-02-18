
"""
get_input module to get values from the command line.

see: https://github.com/lwanger/cooked_input for more information.

Author: Len Wanger
Copyright: Len Wanger, 2017
"""

import sys
import collections
import veryprettytable


def compose(value, funcs):
    """
    Compose functions and return the result: compose(value, [f1,f2,f3]) = f3(f2(f1(value)))

    :param value: the value to apply to funcs (the composed list of functions.)
    :param funcs: a function or list of functions to compose.

    :return: the return value of the functions composed together.
    """
    first_func = True
    result = None

    if callable(funcs):
        result = funcs(value)
    elif isinstance(funcs, collections.Iterable):
        for func in funcs:
            if first_func:
                result = func(value)
                first_func = False
            else:
                result = func(result)
    else:
        raise RuntimeError('funcs cannot be called')

    return result


def make_pretty_table(rows, second_col_name='name', sort_by_second_col=True):
    """
    Take a list of tuples [(id, value), ...] and return a prettytable

    :param rows: a list of tuples for the table rows. Each tuple is: (id, value).
    :param second_col_name: the name to use for the header on the second column.
    :param sort_by_second_col: sort by the second column if True, otherwise leave in order from rows.
    :return: a prettytable for the table.
    """
    #x = prettytable.PrettyTable(['id', second_col_name])
    x = veryprettytable.PrettyTable(['id', second_col_name])

    for row in rows:
        x.add_row([row[0], row[1]])

    x.align[second_col_name] = 'l'  # left align
    x.sortby = second_col_name if sort_by_second_col else 'id'
    return x


def isstring(s):
    """
    An annoyance in Pythons is you can't easily tell something is a string-like thing (string, unicode, bytes, etc.)
    For instance, both 'abc' and ['a', 'b', 'c'] are iterators, but the latter is not a valid password! Further, in
    some cases strings can be of type bytes, which is not caught as a str (Python 3) or basestring (legacy Python) This
    function checks if the value can be treated like a string.

    :param s: the value to check
    :return: True if value is a string-like thing (string, unicode, bytes, etc.), otherwise False
    """

    # if we use Python 3
    if (sys.version_info[0] >= 3):
        return isinstance(s, (str, bytes))
    else:  # we use Legacy Python (2.x)
        return isinstance(s, (basestring, bytes))


def put_in_a_list(values):
    """
    An annoyance in Pythons is you can't easily tell between an iterable (e.g. a list) and a string (i.e. both are
    iterables.) This is a pain if you try to create a list of these things as list('foo') returns ['f', 'o'. 'o'].
    There are also a bunch of cases to take into account now (strings, bytes, unicode, legacy Python) too.
    This routine takes either a single value or list of values and returns a list of those values.

    :param values:
    :return: list containing the values
    """

    if values is None:
        result = []
    elif isstring(values):
        result = [values]
    elif isinstance(values, collections.Iterable):  # list or other iterable
        result = list(values)
    else:  # single non-iterable value
        result = [values]

    return result


def renumerate(sequence):
    """
    Reverse emumerate - starts at the highest index (last item in the iterator) and counts down. This generator yields
    a tuple containing the index and item, starting with the last item in the iterator.

    Don't use reversed(list(enumerate(sequence))) as it's not efficient (it has to iterate through the whole sequence first.)

    :param sequence:
    :return:
    """
    for i in range(len(sequence)-1, -1, -1):
        yield (i, sequence[i])


def swap_element(sequence, idx, replacement):
    """
    Returns a copy of the sequence with the ith value swapped with the replacement value. Useful for immutable values
    such as strings.

    :param sequence: the original immutable sequence.
    :param idx: the index of the sequence element to swap (use negative index to count from last element of the sequence.)
    :param replacement: the replacement value the ith element of the sequence

    :return: a copy of the original sequence with the ith element replaced by the replacement value
    """
    seq_length = len(sequence)

    if seq_length == 0: # return a copy of the empty sequence
        raise ValueError('cannot swap value in an empty sequence')

    if idx < 0:
        use_idx = seq_length + idx
    else:
        use_idx = idx

    if use_idx < 0 or use_idx >= seq_length:
        raise IndexError('index out of range')

    if seq_length == 1: # swap element in a single element sequence
        return replacement
    elif use_idx == 0:  # swap first element
        return replacement + sequence[1:]
    elif use_idx == seq_length-1:   # swap last element
        return sequence[:use_idx] + replacement
    else:   # swap an element in the middle of a sequence
        return sequence[:use_idx] + replacement + sequence[use_idx + 1:]


def cap_last_word(value):
    """
    Capitalize the last word of a string.

    :param value: string to capitalize

    :return: a copy of the string with the last word capitalized.
    """
    last_non_white_char = None

    for i,c in renumerate(value):
        if not c.isspace(): # last_non_white_space = i
            last_non_white_char = c
            continue
        elif last_non_white_char is not None and c.isspace():
            result = value.lower()
            result = swap_element(result, i+1, last_non_white_char.upper())
            return result

    if last_non_white_char is None: # value is all white space, return the original value
        return  value

    # String does not have any white space, so first word is the last word
    return value.capitalize()
