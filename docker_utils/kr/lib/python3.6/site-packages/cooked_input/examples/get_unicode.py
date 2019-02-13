#!/usr/local/bin/python
# coding: latin-1

"""
Use cooked_input tables to create a Unicode character picker. This demonstrates how to use cooked input with large,
mult-column table. It also shows how to used commands for table control.

Len Wanger, 2017
"""

import unicodedata

import cooked_input as ci

try:
    # Try to import pyperclip. If imports then can add the character to the clipboard
    import pyperclip
    USE_CLIPBOARD = True
except (ModuleNotFoundError):
    print('\nWarning: Install the pyperclip module to have the unicode character copied to the clipboard\n')
    USE_CLIPBOARD = False


def unicode_item_filter(item, action_dict):
    """
    Filter table items by category and search string

    action_dict has the following entries controlling filtering:
        cat_filter - filter for the category. if None ignore filter. 'L*' filters any Letter category
        name_filter is a keyword to find the the char name, None for no filter
        item_data ['no_filter'] True then passes filter automatically
    """
    try:
        if item.item_data and item.item_data['no_filter'] is True:
            return (False, True)
    except KeyError:
        pass

    try:
        cat_filter = action_dict['cat_filter']
        in_name = action_dict['name_filter']
    except (KeyError):
        return (False, True)

    cat1 = cat2 = None

    if cat_filter is not None and len(cat_filter) == 2:
        cat1 = cat_filter[0] if cat_filter[0] != '*' else None
        cat2 = cat_filter[1] if cat_filter[1] != '*' else None

    ch_name = item.values[1]
    ch_cat = item.values[2]

    try:
        if (cat1 is None or ch_cat[0]==cat1) and (cat2 is None or ch_cat[1]==cat2) and (in_name is None or in_name in ch_name):
            return (False, True)
    except (IndexError, TypeError):
        pass

    return (True, False)


def help_cmd_action(cmd_str, cmd_vars, cmd_dict):
    print('Unicode picker commands:\n')
    print('?\tshow this help information')
    print('filter\tfilter table rows by category and/or key words')
    print('next\tpage table forward')
    print('prev\tpage table backward')
    print('home\tgo to first row of the table')
    print('end\tgo to last row of the table')
    print_filter_usage('')
    return (ci.COMMAND_ACTION_NOP, None)


def print_filter_usage(cmd_str):
    print('\nFilter command usage: {} [category] [name]'.format(cmd_str))
    print('categories:')
    print('\tLu - letter, u - uppercase, l - lowercase, t - titlecase, m - modifier, 0 - other')
    print('\tMn - mark, n - non-spacing, c - spacing combining, e - enclosing')
    print('\tNd - number, d - decimal digit, l - letter, o - other')
    print('\tPc - punctuation, c - connector, d - dash, s - open, e - close, i - initial quote, f- final quote, 0 - other')
    print('\tSm - symbol, m - math, c - currency, k - modifier, o - other')
    print('\tZd - separator, s - space, l - line, p - paragraph')
    print('\tCc - other, c - control, f - format, s- surrogate, o - private use, n - not assigned')
    print('\n\tUse "*" for either character as a wildcard')
    print()


def filter_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    filter command filter category name
    modifiers:
        Lu - letter, u - uppercase, l - lowercase, t - titlecase, m - modifier, 0 - other
        Mn - mark, n - non-spacing, c - spacing combining, e - enclosing
        Nd - number, d - decimal digit, l - letter, o - other
        Pc - punctuation, c - connector, d - dash, s - open, e - close, i - initial quote, f- final quote, 0 - other
        Sm - symbol, m - math, c - currency, k - modifier, o - other
        Zd - separator, s - space, l - line, p - paragraph
        Cc - other, c - control, f - format, s- surrogate, o - private use, n - not assinged

        This is summed up in regex:
            \*\*|L[ultmo\*]|M[nce\*]|N[dlo\*]|P[cdseifo\*]|S[mcko\*]|Z[slp\*]|C[cfson\*]
    """
    cat_arg = name_arg = None
    variables = cmd_vars.split(' ') if len(cmd_vars) else []
    cat_regex = '\*\*|L[ultmo\*]|M[nce\*]|N[dlo\*]|P[cdseifo\*]|S[mcko\*]|Z[slp\*]|C[cfson\*]'
    category_validator = ci.RegexValidator(pattern=cat_regex)

    if len(variables) > 2:
        print_filter_usage(cmd_str)
        return (ci.COMMAND_ACTION_NOP, None)

    if len(variables) > 0:
        cat_arg = variables[0]

        if len(cat_arg) != 2:
            print_filter_usage(cmd_str)
            return (ci.COMMAND_ACTION_NOP, None)

        name_arg = variables[1] if len(variables) > 1 else None

    if cat_arg is None:
        cat = ci.get_string(prompt='Enter filter value for category', default='**', validators=category_validator)
    else:
        if ci.validate(cat_arg, validators=category_validator):
            cat = cat_arg
        else:
            print_filter_usage(cmd_str)
            return (ci.COMMAND_ACTION_NOP, None)

    if name_arg is None:
        name = ci.get_string(prompt='Enter description keyword filter value', default=name_arg, required=False)
    else:
        name = name_arg

    cmd_dict['cat_filter'] = cat
    cmd_dict['name_filter'] = name
    raise ci.RefreshScreenInterrupt


def make_table(start=32, end=0x007F, cat_filter='**', name_filter=''):
    """
    Creates and returns a cooked_input table containing Unicode characters (with ordinal values from start to end). The
    cat_filter and name_filter are added to the action_dict and used as an item filter for the table. For instance to look
    for letters use cat_filter 'L*', for upper case letters 'Lu', and for currency symbols '*c'. name_filter looks for a
    substring in the unicode character name. For example to fine a latin character use 'LATIN'.

    for start and stop values:

     code charts: https://www.unicode.org/Public/UCD/latest/charts/CodeCharts.pdf
        basic latin: 0000-00FF
        latin extended: 0100-024F
        spacing and modifiers: 02B0-02FF
        greek: 0370-03FF
        hebrew: 0590-05FF
        superscripts and subscripts: 2070-209F
        currency: 20A0-20CF
        math operators: 2200-22FF
        technical: 2300-23FF
        box drawing: 2500-257F
        block elements: 2580-259F
        misc symbols: 2600-26FF
        dingbats: 2700-27BF
        muscial symbols: 1D100-1D1FF
        emoticons: 1F600-1F64F

    utf-8 is: https://en.wikipedia.org/wiki/UTF-8, single octet - 0000-007F
    """
    tis = []
    col_names = "Character Category Name".split()
    for i in range(start,end):
        try:
            ch = chr(i)
            name = unicodedata.name(ch)
            cat = unicodedata.category(ch)
            ti = ci.TableItem(col_values=[ch, name, cat], tag='{:X}'.format(i))  # use hex value as tag
            tis.append(ti)
        except (ValueError) as err:
            name = 'n/a'
        except (UnicodeEncodeError) as err:
            print('UnicodeEncodeError: couldn\'t encode char {}'.format(i))

    ad = {'cat_filter': cat_filter, 'name_filter': name_filter}

    help_cmd = ci.GetInputCommand(help_cmd_action)

    cmds = {'?': help_cmd, 'help': help_cmd,
            'filter': ci.GetInputCommand(filter_cmd_action, cmd_dict=ad),
            'next': ci.GetInputCommand(ci.next_page_cmd_action),
            'prev': ci.GetInputCommand(ci.prev_page_cmd_action),
            'home': ci.GetInputCommand(ci.first_page_cmd_action),
            'end': ci.GetInputCommand(ci.last_page_cmd_action),
        }

    table = ci.Table(rows=tis, col_names=col_names, default_action=ci.TABLE_RETURN_FIRST_VAL,
                     item_filter=unicode_item_filter, action_dict=ad, add_exit=False, commands=cmds)
    ad['table'] = table
    return table


if __name__ == '__main__':
    print('\nUnicode Picker... type "?" for help\n')
    table = make_table(0x00080, 0x007FF, cat_filter='**', name_filter='')
    result = ci.get_table_input(table)

    if USE_CLIPBOARD is True: # put character on the clipboard
        pyperclip.copy(result)
        print('{} copied to the clipboard'.format(result))
    else:
        print('Unicode character={}'.format(result))
