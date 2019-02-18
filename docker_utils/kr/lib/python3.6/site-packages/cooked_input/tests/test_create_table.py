# test create_table:
import sys

if sys.version_info[0] > 2:  # For Python 3
    from io import StringIO
else:
    from StringIO import StringIO


from collections import namedtuple
from cooked_input import create_table, create_rows, Table, TableStyle
from cooked_input import TABLE_RETURN_ROW, TABLE_RETURN_TABLE_ITEM, RULE_FRAME, RULE_ALL

from .utils import redirect_stdin

class Person(object):
    def __init__(self, first, last, age, shoe_size):
        self.first = first
        self.last = last
        self.age = age
        self.shoe_size = shoe_size


def use_create_table(items, fields, field_names, gen_tags, tag_str, item_data=None, add_item_to_item_data=False,
                     add_exit=False, prompt=None, style=None, default_choice=None, default_action=TABLE_RETURN_ROW):

    # prompt = None
    tbl = create_table(items, fields, field_names=field_names, gen_tags=gen_tags, tag_str=tag_str,
                       item_data=item_data,
                       add_item_to_item_data=add_item_to_item_data, add_exit=add_exit, style=style,
                       default_choice=default_choice,
                       default_action=default_action, prompt=prompt)
    print()
    recipe_ti = tbl.get_table_choice(commands=None)
    print(recipe_ti)
    return recipe_ti



class TestTables(object):
    def test_show_table(self):
        people = [
            Person('John', 'Cleese', 78, 14),
            Person('Terry', 'Gilliam', 77, 10),
            Person('Eric', 'Idle', 75, 12),
        ]

        rows = create_rows(people, ['last', 'first', 'shoe_size'])
        Table(rows, ['First', 'Shoe Size'], tag_str='Last').show_table()
        print()

    def test_get_table_choice(self):
        input_str = '1'

        items = {
            1: {"episode": 1, "name": "Whither Canada?", "date": "5 October, 1969", "season": 1},
            2: {"episode": 4, "name": "Owl Stretching Time", "date": "26 October, 1969", "season": 1},
            3: {"episode": 15, "name": "The Spanish Inquisition", "date": "22 September, 1970", "season": 2},
            4: {"episode": 35, "name": "The Nude Organist", "date": "14 December, 1972", "season": 2}
        }

        fields = 'episode name date'.split()
        field_names = 'Episode Name Date'.split()
        tbl = create_table(items, fields, field_names, add_item_to_item_data=True,
                           title='And Now For Something Completely different')

        with redirect_stdin(StringIO(input_str)):
            choice = tbl.get_table_choice()
            item = choice.item_data["item"]
            print('{}: {}'.format(item['name'], item['season']))
        assert (item['name'] == 'Whither Canada?')

    def test_get_table_single_autogen(self):
        # single item list, generate tags
        input_str = '2'

        print('\nTest list of single items - autogen tags\n')
        table_style = TableStyle(show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL)
        items = [["Beast"], ["Deuce"], ["Seth"]]  # single item list
        fields = 'name'.split()
        field_names = 'Name'.split()
        gen_tags = True
        tag_str = ''
        prompt = 'Choose a printer'

        with redirect_stdin(StringIO(input_str)):
            result = use_create_table(items, fields, field_names, gen_tags, tag_str, prompt=prompt, style=table_style)
        assert (result == [2, 'Deuce'])


    def test_get_table_single_autogen(self):
        # single item list
        input_str = 'Beast'

        print('\nTest list of single items (no autogen tags)\n')
        prompt = None
        items = [["Beast"], ["Deuce"], ["Seth"]]  # single item list
        fields = 'name'.split()
        field_names = 'Name'.split()
        table_style = TableStyle(show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL)
        gen_tags = False
        tag_str = 'Printer'
        add_exit = True

        with redirect_stdin(StringIO(input_str)):
            result = use_create_table(items, fields, field_names, gen_tags, tag_str, add_exit=add_exit, prompt=prompt, style=table_style)

        assert (result == ['Beast'])


    # TODO - exit is returning a TableItem, not None.
    def test_get_table_single_autogen(self):
        # single item list
        input_str = 'exit'

        print('\nTest list of single items (no autogen tags)\n')
        prompt = None
        items = [["Beast"], ["Deuce"], ["Seth"]]  # single item list
        fields = 'name'.split()
        field_names = 'Name'.split()
        table_style = TableStyle(show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL)
        gen_tags = False
        tag_str = 'Printer'
        add_exit = True

        with redirect_stdin(StringIO(input_str)):
            result = use_create_table(items, fields, field_names, gen_tags, tag_str, add_exit=add_exit, prompt=prompt, style=table_style)

        print('result is...' + str(result))
        assert (result.action == 'exit')


    def test_single_item_table(self):
        input_str = 'Beast'

        print('\nTest list of single items (no autogen tags)\n')
        prompt = None
        items = [["Beast"], ["Deuce"], ["Seth"]]  # single item list
        fields = 'name'.split()
        field_names = 'Name'.split()
        table_style = TableStyle(show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL)
        gen_tags = False
        tag_str = 'Printer'
        add_exit = True
        with redirect_stdin(StringIO(input_str)):
            result = use_create_table(items, fields, field_names, gen_tags, tag_str, add_exit=add_exit, prompt=prompt, style=table_style)

        print('result is...' + str(result))
        assert (result == ['Beast'])


    def test_multi_item_list(self):
        input_str = 'Ford2'

        print('\nTest list of multiple items (no autogen tags)\n')
        items = [["Beast", "IO-PROD", "Model One G2"], ["Ford2", "Dearborn", "Model One G2.1"],
                 ["Seth", "IO-PROD", "Cell"]]
        fields = 'name location model'.split()
        field_names = 'Name Location IO_Model'.split()
        table_style = TableStyle(show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL)
        gen_tags = False
        tag_str = None
        with redirect_stdin(StringIO(input_str)):
            result = use_create_table(items, fields, field_names, gen_tags, tag_str, style=table_style)
        print('result is...' + str(result))
        # assert (result[0] == 'Ford2' )
        assert (result == ["Ford2", "Dearborn", "Model One G2.1"] )

    def test_dict_of_dicts(self):
        input_str = 'Seth'

        print('\nTest list of dictionary of dictionaries (no autogen tags)\n')
        items = {1: {"name": "Beast", "location": "IO-PROD", "model": "Model One G2"},
                 2: {"name": "Ford2", "location": "Dearborn", "model": "Model One G2.1"},
                 3: {"name": "Seth", "location": "IO-PROD", "model": "Cell"}}
        fields = 'name location model'.split()
        field_names = 'Name Location IO_Model'.split()
        table_style = TableStyle(show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL)
        gen_tags = False
        tag_str = "Printer"
        with redirect_stdin(StringIO(input_str)):
            result = use_create_table(items, fields, field_names, gen_tags, tag_str, style=table_style)
        assert (result == ["Seth", "IO-PROD", "Cell"] )


    def test_dict_of_lists(self):
        input_str = '3'

        print('\nTest list of dictionary of lists (autogen tags)\n')

        items = {1: ["Beast", "IO-PROD", "Model One G2"], 2: ["Ford2", "Dearborn", "Model One G2.1"],
                 3: ["Seth", "IO-PROD", "Cell"]}
        fields = 'name location model'.split()
        field_names = 'Name Location IO_Model'.split()
        table_style = TableStyle(show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL)
        gen_tags = True
        tag_str = "Printer"
        with redirect_stdin(StringIO(input_str)):
            result = use_create_table(items, fields, field_names, gen_tags, tag_str, style=table_style)
        assert (result == [3, "Seth", "IO-PROD", "Cell"] )


    def test_table_of_tablestyles(self):
        input_str = '3'

        print('\nTest list of class instances (autogen tags)\n')

        items = [
            TableStyle(True, True, RULE_FRAME, RULE_FRAME),
            TableStyle(True, False, RULE_FRAME, RULE_FRAME),
            TableStyle(False, True, RULE_ALL, RULE_FRAME),
            TableStyle(False, False, RULE_FRAME, RULE_ALL),
        ]
        fields = 'show_cols hrules vrules'.split()  # no show_border on purpose
        field_names = 'Show_Cols H-Rules V-Rules'.split()
        table_style = TableStyle(show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL)
        gen_tags = True
        tag_str = "Table Style"
        with redirect_stdin(StringIO(input_str)):
            result = use_create_table(items, fields, field_names, gen_tags, tag_str, style=table_style)
        assert (result == [3, False, 1, 0] )


    def test_named_tuple(self):
        input_str = '3'
        print('\nTest list of named tuples (autogen tags)\n')

        MyTuple = namedtuple("MyTuple", "name location model other")
        items = [
            MyTuple("Beast", "IO-PROD", "Model One G2", "Other stuff"),
            MyTuple("Ford2", "Dearborn", "Model One G2.1", "Other stuff"),
            MyTuple("Seth", "IO-PROD", "Cell", "Seth Other stuff"),
        ]
        fields = 'name location model'.split()
        field_names = 'Name Location IO_Model'.split()
        table_style = TableStyle(show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL)
        gen_tags = True
        tag_str = None
        aitid = True
        default_action = TABLE_RETURN_TABLE_ITEM
        with redirect_stdin(StringIO(input_str)):
            ti = use_create_table(items, fields, field_names, gen_tags, tag_str, item_data=None,
                              add_item_to_item_data=aitid, style=table_style, default_action=default_action)

        print(f'name={ti.item_data["item"].name},  other={ti.item_data["item"].other}')
        assert (ti.item_data['item'].name == 'Seth')
        assert (ti.tag == 3)
