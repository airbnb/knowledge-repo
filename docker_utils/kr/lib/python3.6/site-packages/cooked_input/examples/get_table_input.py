"""
cooked input examples of getting inputs from tables

Len Wanger, 2017

TODO - show examples of
    - dynamic table
    - title, header and footer
    - item_data
    - rows_per_page
    - enabled/disabled
    - filtered
    - actions
    - navigation keys/commands
"""

from cooked_input import get_table_input, Table, TableItem, TableStyle, get_menu, TABLE_RETURN_FIRST_VAL
from cooked_input import RULE_ALL, RULE_FRAME, RULE_HEADER, RULE_NONE


def return_color_str_action(row, action_dict):
    return row.values[0]


def red_action(row, action_dict):
    if action_dict['live'] is True:
        return 'Live is True!'
    else:
        return 'Better dead than red!'


def return_rgb_action(row, action_dict):
    return row.values[2]


if __name__ == '__main__':
    table_items = [
        TableItem('red'),
        TableItem('blue'),
        TableItem('green'),
    ]

    style_1 = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)

    # simplest way
    table = Table(table_items, col_names=['Color'])
    tag = get_table_input(table)
    print('\ntag={}\n'.format(tag))

    # simplest way (style -- no borders)
    table = Table(table_items, col_names=['Color'], style=style_1)
    tag = get_table_input(table)
    print('\ntag={}\n'.format(tag))

    # get value from table with specified default action (get values[0] - color name)
    table = Table(table_items, col_names=['Color'], default_action=TABLE_RETURN_FIRST_VAL, prompt='Color? (Table prompt) ')
    color_str = get_table_input(table)
    print('\ncolor_str={}\n'.format(color_str))

    # custom action for default table action and on a table item (red)
    table_items[0] = TableItem('red', action=red_action)
    table = Table(table_items, col_names=['Color'], default_action=return_color_str_action, action_dict={'live': False})
    color = get_table_input(table, prompt='Color id')
    print('\ncolor={}\n'.format(color))

    # running the table (loop until exit)
    print('running table...')
    table = Table(table_items, col_names=['Color'], add_exit=True, default_action=TABLE_RETURN_FIRST_VAL, prompt='Color? (Table prompt) ')
    table.run()
    print('\ndone running table...\n')

    # test default choice
    result = get_menu(['red', 'green', 'blue'], title='Colors', prompt='Choose a color', default_choice='blue', add_exit=False)
    print('result={}'.format(result))

    # Test multiple columns
    table_items = [
        TableItem(['red', 'roses are red', (255,0,0)]),
        TableItem(['blue', 'violets are blue', (0,255,0)]),
        TableItem(['green', 'green is the color of my true love\'s eyes', (0,0,255)]),
    ]

    table = Table(table_items, col_names=['Color', 'Ode', 'RGB'], default_action=return_rgb_action)
    rgb = get_table_input(table, prompt='Enter the id of the color you want',
                            convertor_error_fmt='not a valid color id',
                            validator_error_fmt='not a valid color id')
    print('rgb={}, r={}, g={}, b={}'.format(rgb, rgb[0], rgb[1], rgb[2]))



