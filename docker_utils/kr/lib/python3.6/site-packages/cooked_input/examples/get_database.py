"""
cooked input example showing how to use with entries from database tables.

Len Wanger, 2017
"""

import sqlite3
from collections import Counter
import cooked_input as ci

def create_db():
    # Create an in memory sqlite database of hamburger options
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()

    # Create tables
    c.execute('''CREATE TABLE buns (id INTEGER PRIMARY_KEY, type text, price real)''')
    c.execute("INSERT INTO buns VALUES (1, 'plain' ,1.00)")
    c.execute("INSERT INTO buns VALUES (2, 'sesame seed', 1.25)")
    c.execute("INSERT INTO buns VALUES (3, 'pretzel', 1.50)")

    c.execute('''CREATE TABLE patties (id INTEGER PRIMARY_KEY, type text, price real)''')
    c.execute("INSERT INTO patties VALUES (1, 'hamburger' ,1.00)")
    c.execute("INSERT INTO patties VALUES (2, 'sirloin' ,2.00)")
    c.execute("INSERT INTO patties VALUES (3, 'chicken', 1.50)")
    c.execute("INSERT INTO patties VALUES (4, 'veggie', 1.50)")

    c.execute('''CREATE TABLE extras (id INTEGER PRIMARY_KEY, type text, price real)''')
    c.execute("INSERT INTO extras VALUES (1, 'bacon', 1.00)")
    c.execute("INSERT INTO extras VALUES (2, 'cheese', 1.00)")
    c.execute("INSERT INTO extras VALUES (3, 'special sauce', 0.0)")
    c.execute("INSERT INTO extras VALUES (4, 'tomatoes', 0.50)")
    c.execute("INSERT INTO extras VALUES (5, 'grilled onions', 0.75)")
    c.execute("INSERT INTO extras VALUES (6, 'lettuce', 0.0)")
    c.execute("INSERT INTO extras VALUES (7, 'pickles', 0.0)")

    conn.commit()
    return conn, c


def table_item_factory(row):
    values = [row[1], '${:.2f}'.format(row[2])]
    ti = ci.TableItem(values, item_data={'price': row[2]})
    return ti


def build_a_burger_v2(conn):
    price = 0.0
    col_names = '# Type'

    # Get the bun type
    prompt_str = 'Which kind of bun do you want'
    def_choice_str = ' (plain)'
    cursor.execute('SELECT * FROM buns ORDER BY price')
    tis = [table_item_factory(row) for row in cursor]
    tbl = ci.Table(tis, col_names=col_names.split(), title=None, prompt=prompt_str, default_choice=1,
                   default_str=def_choice_str, add_exit=False, default_action='table_item')
    bun = tbl.get_table_choice()
    price += bun.item_data['price']

    # Get the patty type
    prompt_str = 'Which kind of patty do you want'
    def_choice_str = ' (hamburger)'

    cursor.execute('SELECT * FROM patties ORDER BY price')
    tis = [table_item_factory(row) for row in cursor]
    tbl = ci.Table(tis, col_names=col_names.split(), title=None, prompt=prompt_str, default_choice=1,
                   default_str=def_choice_str, add_exit=False, default_action='table_item')
    patty = tbl.get_table_choice()
    price += patty.item_data['price']

    # Get the options - note: allow an arbitrary of options, and keep track of how many of each
    prompt_str = 'Which kind of extra do you want (hit return when done choosing extras)'
    extras = []
    cursor.execute('SELECT * FROM extras')
    tis = [table_item_factory(row) for row in cursor]
    tbl = ci.Table(tis, col_names=col_names.split(), title=None, prompt=prompt_str, add_exit=False,
                   default_action='table_item', required=False, refresh=False)

    while True:
        choice = tbl.get_table_choice()

        if choice is None:
            break
        else:
            extras.append(choice)
            price += choice.item_data['price']

    option_counter = Counter(extras)

    print('\nSummary of your burger:')
    print('=======================\n')
    print('{} bun: ${:.2f}'.format(bun.values[0], bun.item_data['price']))
    print('{} patty: ${:.2f}'.format(patty.values[0], patty.item_data['price']))

    if len(extras) == 0:
        print('No extras:')
    else:
        print('Extras:')
        for extra, count in option_counter.items():
            if count == 1:
                print('\t{}: ${:.2f}'.format(extra.values[0], extra.item_data['price']))
            else:
                print('\t{}x {}: ${:.2f}'.format(count, extra.values[0], extra.item_data['price']))

    return price


if __name__ == '__main__':
    conn, cursor = create_db()

    print('\nBuild your burger!')
    print('==================\n')
    price = build_a_burger_v2(conn)
    print('\ntotal price: \t${:.2f}'.format(price))

    conn.close()
