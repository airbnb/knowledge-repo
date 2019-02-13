from __future__ import print_function

"""
get_table - table/menu system for cooked_input

TODO:
    - navigation keys - looking for a good solution to capture keys like PageDown and bind them to functions. Curses 
        doesn't come on Windows.
    - Add more formatting to tables - borders, text styles, foreground and background colors, title, header, footer. 

Len Wanger, 2017
"""

import sys
import string

import veryprettytable as pt

from cooked_input import get_input
from cooked_input import GetInputInterrupt, RefreshScreenInterrupt
from cooked_input import PageUpRequest, PageDownRequest, FirstPageRequest, LastPageRequest, UpOneRowRequest, DownOneRowRequest

from .input_utils import put_in_a_list, isstring
from .cleaners import CapitalizationCleaner, StripCleaner, ChoiceCleaner
from .convertors import ChoiceConvertor
from .validators import ChoiceValidator


# Enumerated values for tables:
TABLE_ITEM_DEFAULT = 'default'
TABLE_ITEM_EXIT = 'exit'
TABLE_ITEM_RETURN = 'return'

TABLE_ADD_EXIT = 'exit'
TABLE_ADD_RETURN = 'return'
TABLE_ADD_NONE = 'none'

TABLE_RETURN_TAG = 'tag'
TABLE_RETURN_FIRST_VAL = 'first_value'
TABLE_RETURN_ROW = 'row'
TABLE_RETURN_TABLE_ITEM = 'table_item'

RULE_FRAME = pt.FRAME
RULE_HEADER = pt.HEADER
RULE_ALL = pt.ALL
RULE_NONE = pt.NONE


# Supplied table actions
def return_table_item_action(row, action_dict):
    """
    Action function for Tables. This function returns the TableItem instance. Used by the **TABLE_RETURN_TABLE_ITEM** action.

    :param List row: the data associated with the selected row
    :param Dict action_dict: the dictionary of values associated with the action - ignored in this function

    :return: A list containing all of the data for the selected row of the table.
    :rtype: List
    """
    return row


def return_row_action(row, action_dict):
    """
    Default action function for Tables. This function returns the whole row of data including the tag. Used by
    the **TABLE_RETURN_ROW** action.

    :param List row: the data associated with the selected row
    :param Dict action_dict: the dictionary of values associated with the action - ignored in this function

    :return: A list containing all of the data values for the selected row of the table.
    :rtype: List
    """
    return [row.tag] + row.values


def return_tag_action(row, action_dict):
    """
    Default action function for tables. This function returns the tag for the row of data. Used by the **TABLE_RETURN_TAG** action.

    :param List row: the data associated with the selected row
    :param Dict action_dict: the dictionary of values associated with the action - ignored in this function

    :return: The tag for the selected row of the table.
    """
    return row.tag


def return_first_col_action(row, action_dict):
    """
    Default action function for tables. This function returns the first data column value for the row of
        data. Used by the **TABLE_RETURN_FIRST_VAL** action.

    :param List row: the data associated with the selected row
    :param Dict action_dict: the dictionary of values associated with the action - ignored in this function

    :return: The first value from the list of data values for the selected row of the table.
    """
    return row.values[0]


# command actions for supporting table pagination
def first_page_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to show the first (home) page in a paginated table. This command raises a :class:`FirstPageRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise FirstPageRequest


def last_page_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to show the last (end) page in a paginated table. This command raises a :class:`LastPageRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise LastPageRequest


def next_page_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to show the next page in a paginated table. This command raises a :class:`PageDownRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise PageDownRequest


def prev_page_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to show the previous page in a paginated table. This command raises a :class:`PageUpRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise PageUpRequest


def scroll_up_one_row_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to scroll up one row in a paginated table. This command raises a :class:`UpOneRowRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise UpOneRowRequest


def scroll_down_one_row_cmd_action(cmd_str, cmd_vars, cmd_dict):
    """
    Command action to scroll down one row in a paginated table. This command raises a :class:`DownOneRowRequest`
    exception.

    :param cmd_str:  ignored
    :param cmd_vars: ignored
    :param cmd_dict: ignored
    :return: None
    """
    raise DownOneRowRequest


#
# Class definitions for tables
#
class TableStyle():
    """
    ``TableStyle`` is used to define the visual style of a ``Cooked_Input`` table. :class:`Table` objects take an
    instance of ``TableStyle`` as the style parameter.

    :param Bool show_cols: if **True** (default) shows a the column names at the top of the table
    :param Bool show_border: if **True** (default) shows a border around the table
    :param hrules: whether to draw horizontal lines between rows. See below for allowed RULE values.
    :param vrules: whether to draw vertical lines between rows. See below for allowed RULE values.
    :param int rows_per_page: The maximum number of rows to display in the table. Used for paginated tables.

    ``hrules`` and ``vrules`` can use the following ``RULE`` values for the rows and columns respectively:

        +-------------+-------------------------------------------------------------------+
        | value       | action                                                            |
        +-------------+-------------------------------------------------------------------+
        | RULE_FRAME  | Draw ruled lines around the outside (frame) of the table.         |
        | RULE_HEADER | Draw ruled lines around the header of the table.                  |
        | RULE_ALL    | Draw ruled line around the table, header and between columns/rows.|
        | RULE_NONE   | Do not draw any rules lines around columns/rows.                  |
        +-------------+-------------------------------------------------------------------+
    """
    def __init__(self, show_cols=True, show_border=True, hrules=RULE_FRAME, vrules=RULE_ALL, rows_per_page=20):
        self.show_cols = show_cols
        self.show_border = show_border
        self.hrules = hrules
        self.vrules = vrules
        self.rows_per_page = rows_per_page
        #TODO -- add:   header fmt str, footer fmt str, alignment, tag_alignment.


class TableItem(object):
    """
    TableItem is used to represent individual rows in a table. This is also often used for menu items.

    :param List col_values: A list of values for the row's columns.
    :param tag:  a value used to choose the item. If None, a default tag will be assigned by the :class:`Table`.
    :param Callable action:  an action function called when the item is selected.
    :param Dict item_data: a dictionary containing addtional contextual data for the table row. This is
        not displayed as part of the table item but can be used for processing actions. For example, ``item_data`` can
        store the database ID associated for the item. ``item_data`` is also used for item filters.
    :param bool hidden: The table row is hidden if **True**, or visible if **False** (default). Hidden table items
        are still selectable, unless the enabled attribute is **False**.
    :param bool enabled: The table row is selectable if **True **(default), and not selectable if **False**.

    TableItem actions:

        The table item action specifies what to do when a table item is selected. The ``action`` can be one of the
        default actions listed in the following table or a custom action can be provided:

        +--------------------------+--------------------------------------------------------------------------+
        | value                    | action                                                                   |
        +--------------------------+--------------------------------------------------------------------------+
        | TABLE_RETURN_TAG         | return the selected row's tag.                                           |
        +--------------------------+--------------------------------------------------------------------------+
        | TABLE_RETURN_FIRST_VAL   | return the first data column value of the selected row.                  |
        +--------------------------+--------------------------------------------------------------------------+
        | TABLE_RETURN_ROW         | return the list of column values for the selected row.                   |
        +--------------------------+--------------------------------------------------------------------------+
        | TABLE_RETURN_TABLE_ITEM  | return the TableItem instance for the selected row.                      |
        +--------------------------+--------------------------------------------------------------------------+
        | TABLE_ITEM_DEFAULT       |  use default method to handle the table item (e.g. use the parent        |
        |                          |  table's default_action handler function)                                |
        +--------------------------+--------------------------------------------------------------------------+
        | TABLE_ITEM_EXIT          |  selecting the table row should exit (used to exit a menu)               |
        +--------------------------+--------------------------------------------------------------------------+
        | TABLE_ITEM__RETURN       |  selecting the table row should return (used to return from a submenu)   |
        +--------------------------+--------------------------------------------------------------------------+

        In addition to the values in the table above, the action can be any callable that takes the following
        parameters:

            * **row** (TableItem) -- The ``TableItem`` instance selected (i.e. this table item)
            * **action_dict** (Dict) --  The parent table's ``action_dict``.
    """
    def __init__(self, col_values, tag=None, action=TABLE_ITEM_DEFAULT, item_data=None, hidden=False, enabled=True):

        self.values = put_in_a_list(col_values)
        self.tag = tag
        self.action = action
        self.item_data = item_data
        self.hidden = hidden
        self.enabled = enabled

    def __repr__(self):
        return 'TableItem(col_values={}, tag={}, action={}, item_data={}, hidden={}, enabled={})'.format(self.values,
                                                    self.tag, self.action, self.item_data, self.hidden, self.enabled)


class Table(object):
    """
    The Table class is used to display a table of data. Each row of data has the same number of
    columns (specified by the ``col_name`` parameter) as is represented by a :class:`TableItem` instance. Tables are
    often used for menus.

    :param List rows: The rows of the table. Each row is a :class:`TableItem` instance.
    :param List col_names: An optional list of the column names (strings) for the table. If no list is given the number
        of columns is determined by the length of the data list for the first row (:class:`TableItem`).
    :param str title: An optional title for the table.
    :param str prompt: The prompt for choosing a table value.
    :param str default_choice: An optional default tag value to use for the table selection.
    :param str default_str: An optional string to display for the default table selection.
    :param Callable default_action: The default action function to call a table item is selected. See below for details.
    :param TableStyle style: a :class:`TableStyle` defining the look of the table.
    :param Dict options: see below for a list of valid options

    Options:

        **required**:    requires an entry if **True**, exits the table on blank entry if **False**.
        
        **tag_str**:     string to use for the tag column name. Defaults to an empty string ("").

        **add_exit**:    automatically adds a :class:`TableItem` to exit the table menu (``TABLE_ITEM_EXIT``) or
                            return to the parent table/menu (``TABLE_ADD_RETURN``), or not to add a :class:`TableItem` at all (**False**).
                            Used to exit menus or return from sub-menus.

        **action_dict**: a dictionary of values to pass to action functions. Used to provide context to
                            the action. Helpful to provide items such as data base sessions, user credentials, etc.

        **case_sensitive**:  whether choosing table items should be case sensitive (**True**) or not (**False** - default)

        **commands**:    a dictionary of commands for the table. For each entry, the key is the command and the
                            value the action to take for the command. See :class:`GetInput` and :class:`GetInputCommand`
                            for further details

        **item_filter**: a function used to determine which table items to display. Displays all items if **None**.
                            See below for more details.

        **refresh**: refresh table items each time the table is shown (**True** - default), or just when created
                            (**False**). Useful for dynamic tables

        **header**:  a format string to print before the table, can use any value from ``action_dict`` as well as
                            pagination information

        **footer**:  a format string to print after the table, can use any values from ``action_dict`` as well as
                            pagination information

    Table default actions:

        Each table has a default action to take when an item is selected. The action can be a callable or a value from
        the table below. The Table's default action is called if the If the selected row (TableItem) has its action
        set to TABLE_DEFAULT_ACTION, otherwise the action for the selected TableItem is called. Standard values for the
        Table default action are:

        +--------------------------+---------------------------------------------------------+
        | value                    | action                                                  |
        +--------------------------+---------------------------------------------------------+
        | TABLE_RETURN_TAG         | return the selected row's tag.                          |
        +--------------------------+---------------------------------------------------------+
        | TABLE_RETURN_FIRST_VAL   | return the first data column value of the selected row. |
        +--------------------------+---------------------------------------------------------+
        | TABLE_RETURN_ROW         | return the list of column values for the selected row.  |
        +--------------------------+---------------------------------------------------------+
        | TABLE_RETURN_TABLE_ITEM  | return the TableItem instance for the selected row.     |
        +--------------------------+---------------------------------------------------------+

        In addition to the values in the table above, the action can be any callable that takes the following
        parameters:

            * **row** (TableItem) -- The :class:`TableItem` instance selected (i.e. this table item)
            * **action_dict** (Dict) --  The parent table's action_dict.

            For example::

                def reverse_tag_action(row, action_dict):
                    if action_dict['reverse'] is True:
                        return row.tag[::-1]
                    else
                        return row.tag

    item filters:

        The item filter option provides a function that determines which table items are hidden and/or enabled in
        the table. It is a callable that takes the following input parameters:

            * **item** (TableItem) --   the :class:`TableItem` instance
            * **action_dict** (Dict) -- the action_dict for the :class:`Table`

        The ``item_filter`` function returns a tuple of two Booleans ``(hidden, enabled)`` for the item (``TableItem``).

        For example, a menu can have choices that are visible and enabled only for user's who are part of the
        administrator group::

            def user_role_filter(row, action_dict):
                if row.item_data is None:
                    return  (False, True)   # visible and enabled

                for role in action_dict['user_roles'].roles:
                    if role in row.item_data['roles']:
                        return  (False, True)   # visible and enabled

                return (True, False)    # hidden and disabled

            action_dict = {'user_roles': ['admin', 'users']}
            admin_only = {'roles': {'admin'} }

            rows = [
                TableItem('Add a new user', action=user_add_action, item_data=admin_only)
                TableItem('list users', action=user_list_action) ]
            menu = Table(menu_items=rows, action_dict=action_dict, item_filter=user_role_filter)
    """
    def __init__(self, rows, col_names=None, title=None, prompt=None, default_choice=None, default_str=None,
                 default_action=None, style=None, **options):

        try:
            self.required = options['required']
        except KeyError:
            self.required = True

        try:
            self.tag_str = options['tag_str']
        except KeyError:
            self.tag_str = ''

        try:
            add_exit = options['add_exit']
            if add_exit in { True, False, TABLE_ADD_EXIT, TABLE_ADD_RETURN }:
                self.add_exit = add_exit
            else:
                print('Table:__init__: ')
                raise RuntimeError('Table: unexpected value for add_exit option ({})'.format(add_exit))
        except KeyError:
            self.add_exit = TABLE_ADD_NONE

        try:
            self.action_dict = options['action_dict']
        except KeyError:
            self.action_dict = {}

        try:
            self.case_sensitive = options['case_sensitive']
        except KeyError:
            self.case_sensitive = False

        try:
            self.commands = options['commands']
        except KeyError:
            self.commands = None

        try:
            self.refresh = options['refresh']
        except KeyError:
            self.refresh = True

        try:
            self.item_filter = options['item_filter']
        except KeyError:
            self.item_filter = None

        try:
            self.header = options['header']
        except KeyError:
            self.header = None

        try:
            self.footer = options['footer']
        except KeyError:
            self.footer = None

        if prompt is None:
            self.prompt = 'Choose a table item'
        else:
            self.prompt = prompt

        self.options = options
        self.title = title
        self.default_choice = default_choice
        self.default_str= default_str

        if default_action is None or default_action == 'tag':
            self.default_action = return_tag_action
        elif default_action == 'first_value':
            self.default_action = return_first_col_action
        elif default_action == 'row':
            self.default_action = return_row_action
        elif default_action == 'table_item':
            self.default_action = return_table_item_action
        else:
            self.default_action = default_action

        if style is None:
            self.style = TableStyle()
        else:
            self.style = style

        self.rows_per_page = self.style.rows_per_page
        self._table_items = put_in_a_list(rows)  # the original, raw table items for the table
        self._rows = []  # the expanded, refreshed table items for the table used to create the pretty table
        self.table = pt.VeryPrettyTable()  # the pretty table to display

        if col_names is None:
            num_cols = len(self._table_items[0].values)
            field_names = ['col {}'.format(i) for i in range(1, num_cols+1)]
        elif isstring(col_names):
            field_name_list = col_names.split()
            field_names = field_name_list
            num_cols = len(field_name_list)
        else:
            field_names = col_names
            num_cols = len(field_names)

        if len(field_names) != num_cols:
            raise RuntimeError('Table: number of column names does not match number of columns in the table'.format())

        self.field_names = [self.tag_str] + field_names
        self.table.field_names = [self.tag_str] + field_names + ['action']

        #self.table.set_style(pt.PLAIN_COLUMNS)
        self.table.set_style(pt.DEFAULT)
        self.table.border = self.style.show_border
        self.table.header = self.style.show_cols
        self.table.align = 'l'
        self.table.align[self.tag_str] = 'r'
        # self.tbl.left_padding_width = 2
        self.table.hrules = self.style.hrules
        self.table.vrules = self.style.vrules

        if self.refresh is False:   # set up rows to start as won't be refreshed each time called
            self.refresh_items(rows=rows, add_exit=True, item_filter=self.item_filter)

        self.show_rows(0)


    def __repr__(self):
        return 'Table(rows={}, col_name={}, title={}, prompt={}, default_choice={}, action_dict={})'.format(self._table_items,
                                            self.field_names, self.title, self.prompt, self.default_choice, self.action_dict)

    def get_num_rows(self):
        """
        Get the number of rows in the table.

        :return: the number of rows in the table
        :rtype: int
        """
        return len(self._rows)

    def get_row(self, tag):
        """
        Get the number of rows in the table.

        :return: the number of rows in the table
        :rtype: :class:`TableItem`
        """
        for row in self._rows:
            if row.tag == tag:
                return row
        raise ValueError('Table.get_row: tag ({}) not in the table'.format(tag))

    def get_action(self, tag):
        """
        Return the action callback function for the first row matching the specified tag.

        :param tag: the tag to search for
        :return: the action for the first row containing the tag. Raises a **ValueError** exception if the tag is not found
        :rtype: Callable
        """
        row = self.get_row(tag)
        return row.action

    def do_action(self, row):
        """
        Call the action function for the specified row

        :param TableItem row: the table row to call the action on
        :return:  returns the return value for the action. Returns the original row if no action is defined for the row.

        The action function is called with the following parameters:

            * **row** -- The :class:`TableItem` instance selected (i.e. this table item)
        """
        action = row.action
        if callable(action):
            return action(row, self.action_dict)
        elif action == 'default' and self.default_action is not None:
            return self.default_action(row, self.action_dict)
        else:
            return row

    def show_rows(self, start_row):
        """
        Set the starting row for to display in the table. Last row shown is the ``start_row`` plus the number of
        rows per page (or the last row if ``start_row`` is within ``rows_per_page`` of the end of the table).

        :param int start_row: the first row of the table to show

        :return: None
        """
        # set the starting and ending rows to show
        table_max_rows = self.get_num_rows()
        if start_row > table_max_rows - self.rows_per_page:
            start_row = table_max_rows - self.rows_per_page

        if start_row < 1:
            self.table.start = 0
        else:
            self.table.start = start_row

        table_end = self.table.start + self.rows_per_page
        if table_end > table_max_rows:
            table_end = table_max_rows

        self.table.end = table_end

    # def refresh_buffer(self, buffer):
    #     if buffer:
    #         buffer.text = self.table.get_string()
    #     else:
    #         print(self.table.get_string())
    #         print()
    #         raise RefreshScreenInterrupt


    def page_up(self):
        """
        Display the previous page of the table (if available)

        :return: None
        """
        self.show_rows(self.table.start - self.rows_per_page)
        print(self.table.get_string())

    def page_down(self):
        """
        Display the next page of the table (if available)

        :return: None
        """
        self.show_rows(self.table.start + self.rows_per_page)
        print(self.table.get_string())

    def goto_home(self):
        """
        Display the first page of the table

        :return: None
        """
        self.show_rows(0)
        print(self.table.get_string())

    def goto_end(self):
        """
        Display the last page of the table

        :return: None
        """
        self.show_rows(self.get_num_rows() - self.rows_per_page)
        print(self.table.get_string())

    def scroll_up_one_row(self):
        """
        Display the one row earlier in the table (if available)

        :return: None
        """
        self.show_rows(self.table.start + 1)
        print(self.table.get_string())

    def scroll_down_one_row(self):
        """
        Display the one row later in the table (if available)

        :return: None
        """
        self.show_rows(self.table.start - 1)
        print(self.table.get_string())


    def _prep_get_input(self, force_refresh=False):
        """
        Internal function to prepare the table for getting input. Refreshes the tabl (for dynamic tables) and prepares
        the choices, cleaners, covertor and validators.

        :return: a tuple of (choices, cleaners, convertor, validator) to use for getting input from the table.
        """
        if self.refresh or force_refresh:
            self.refresh_items(self._table_items, self.add_exit, self.item_filter)

        if self.case_sensitive:
            choices = {str(item.tag): i for i, item in enumerate(self._rows) if item.enabled is True}
        else:
            choices = {str(item.tag).lower(): i for i, item in enumerate(self._rows) if item.enabled is True}

        cleaners = [StripCleaner()]
        if not self.case_sensitive:
            cleaners.append(CapitalizationCleaner('lower'))
        cleaners.append(ChoiceCleaner(choices))

        convertor = ChoiceConvertor(choices)
        validators = ChoiceValidator(choices.values())

        return choices, cleaners, convertor, validators

    def refresh_screen(self):
        """
        Display the current page of the table (including any header or footer)

        :return: None
        """
        formatter = string.Formatter()

        # print header
        if self.header:
            print(formatter.vformat(self.header, None, self.action_dict))

        # print table
        if self.title is not None:
            print('{}'.format(self.title))

        print(self.table.get_string(fields=self.field_names))  # don't show action

        # print footer
        if self.footer:
            print(formatter.vformat(self.footer, None, self.action_dict))


    def show_table(self):
        """
        Show the table without asking for input.

        :return: None
        """
        if self.refresh is True:
            self.refresh_items(self._table_items, self.add_exit, self.item_filter)

        self.refresh_screen()


    def _get_choice(self, table_choices, table_cleaners, table_convertor, table_validators, **options):
        """
        Internal function to get the input for the table choice.

        :param table_cleaners:
        :param table_convertor:
        :param table_validators:
        :param options:

        :return:  the table row for the choice picked
        """
        gi_options = {}
        gi_options['prompt'] = self.prompt
        gi_options['required'] = self.required
        gi_options['default'] = self.default_choice
        gi_options['default_str'] = self.default_str
        gi_options['commands'] = self.commands
        for k,v in options.items():
            gi_options[k] = v

        while True:
            try:
                self.refresh_screen()
                result = get_input(cleaners=table_cleaners, convertor=table_convertor, validators=table_validators, **gi_options)

                if result is None:
                    return None
                else:
                    return self._rows[result]
            except (FirstPageRequest):
                self.goto_home()
            except (LastPageRequest):
                self.goto_end()
            except (PageUpRequest):
                self.page_up()
            except (PageDownRequest):
                self.page_down()
            except (UpOneRowRequest):
                self.scroll_up_one_row()
            except (DownOneRowRequest):
                self.scroll_down_one_row()
            except (RefreshScreenInterrupt):
                table_choices, table_cleaners, table_convertor, table_validators = self._prep_get_input(force_refresh=True)
                self.show_rows(0)

    def get_table_choice(self, **options):
        """
        Prompts the user to choose a value from the table. This is the main method used to choose a value from a table.

        :param options: See below for details.

        :return: the result of performing the action (specified by the table or row) on the row. Returns **None** if no
            row is selected.

        Options:

            * **prompt** (str) -- the prompt for choosing a table value.
            * **required** (bool) -- requires an entry if **True**, exits the table on blank entry if **False**.
            * **default** (str) -- the default value to use.
            * **default_str** (str) -- An optional string to display for the default table selection.
            * **commands** (Dict) -- a dictionary of commands for the table. For each entry, the key is the
                    command and the value the action to take for the command. See :class:`GetInput` and
                    :class:`GetInputCommand` for further details
        """
        table_choices, table_cleaners, table_convertor, table_validators = self._prep_get_input()
        self.show_rows(0)
        row = self._get_choice(table_choices, table_cleaners, table_convertor, table_validators, **options)

        if row is None:
            return None
        else:
            return self.do_action(row)


    def refresh_items(self, rows=None, add_exit=False, item_filter=None):
        """
        Refresh which rows of the table are enabled and shown. Used to update rows in the table. Adds tags if
        necessary. `formatter <https://docs.python.org/3.6/library/formatter.html>`_ is used so values can be
        substituted in format strings from ``action_dict`` using `vformat <https://docs.python.org/2/library/string.html#string.Formatter>`_.
        This is useful in case some TableItems have dynamic data. Can also be used by action to change table items.
        For instance a search action might filter for row entries using an item filter.

        :param List rows: a list of rows to show. If **None**, will use all rows.
        :param bool add_exit: if **TABLE_ADD_EXIT** add an entry to exit, if **TABLE_ADD_RETURN** add an entry to
                            return. Don't add an entry if **False** (default).
        :param Callable item_filter: an optional function used to filter rows. See :class:`Table` for details regarding item filters.

        :return: None
        """
        formatter = string.Formatter()

        if rows is None:
            use_rows = self._table_items
        elif isinstance(rows, TableItem):  # single item, not list
            use_rows = [rows]
        else:
            use_rows = rows

        self.table.clear_rows()
        self._rows = []

        table_idx = 1

        table_items = []
        for item in use_rows:
            table_items.append(item)

        if item_filter is None or item_filter is True:
            filtered_items = table_items
        elif callable(item_filter):
            filtered_items = []
            for item in table_items:
                # could set hidden and enabled directly, but it's easy to forget to return the tuple so warn the user...
                filter_result = item_filter(item, self.action_dict)
                try:
                    item.hidden, item.enabled = filter_result[0], filter_result[1]
                except TypeError:
                    raise RuntimeError('get_table: item_filter needs to return a tuple (hidden, enabled)')
                if item.hidden is False:
                    filtered_items.append(item)

        for item in filtered_items:
            if item.tag is None:
                tag = table_idx
            else:
                tag = item.tag

            item_values = []
            for v in item.values:
                if isstring(v):
                    try:
                        formatted_val = formatter.vformat(str(v), None, self.action_dict)
                    except ValueError: # a curly brace in the value causes a ValueError exception. Double it up to fix this.
                        v2 = str(v).replace('}', '}}').replace('{', '{{')
                        formatted_val = formatter.vformat(str(v2), None, self.action_dict)

                    item_values.append(formatted_val)
                else:
                    item_values.append(v)

            row_entry = TableItem(item_values, tag, item.action, item_data=item.item_data, hidden=item.hidden, enabled=item.enabled)

            self._rows.append(row_entry)
            table_idx += 1

        if add_exit not in (False, 'none') and self.add_exit not in (False, 'none'):
            num_values = 1
            if len(self._rows):
                num_values = len(self._rows[0].values)
            row_values = ['' for i in range(num_values)]
           
            if self.add_exit in (TABLE_ADD_EXIT, True):
                row_tag, row_action = 'exit', TABLE_ITEM_EXIT
            elif self.add_exit == TABLE_ADD_RETURN:
                row_tag, row_action = 'return', TABLE_ITEM_EXIT

            row_entry = TableItem(row_values, row_tag, row_action)

            self.table.add_row([row_entry.tag] + row_entry.values + [row_entry.action])
            self._rows.append(row_entry)

        # refresh table
        self.table.clear_rows()
        table_idx = 1
        for r in self._rows:
            if r.hidden is not True:
                self.table.add_row([r.tag] + r.values + [r.action])
            table_idx += 1

        if self.table.start > self.get_num_rows():
            # filtering can cause the table to not show any rows. If so, show last page of filtered table
            start_row = max(self.get_num_rows() - self.rows_per_page, 0)
            self.show_rows(start_row)

        self.table.end = self.table.start + self.rows_per_page


    def __call__(self, choice=None, action_dict=None):
        """
        Call the run method on the table.

        Note: choice and action_dict parameters are placeholders (ignored) so Tables can be used as action items
        in TableItems. This allows a Table instance to be used as a sub-menu by adding it as the action in a menu
        item.

        :param choice:
        :param action_dict:

        :return: the status from run.
        """
        return self.run()


    def run(self):
        """
        Continue to get input from the table until a blank row (**None**) is returned, or a :class:`GetInputInterrupt`
            exception is raised. This is primarily used to use tables as menus. Choosing exit or return in a menu is
            the same as returning no row.

        :return: **True** if exited without an error, or **False** if a :class:`GetInputInterrupt` exce[tion was raised
        """
        table_choices, table_cleaners, table_convertor, table_validators = self._prep_get_input()
        self.show_rows(0)

        options = {'prompt': self.prompt}

        while True:
            try:
                choice = self._get_choice(table_choices, table_cleaners, table_convertor, table_validators, **options)
            except (GetInputInterrupt) as gii:
                print('\n{}\n'.format(gii))
                continue

            if choice is None:
                action - TABLE_ITEM_EXIT
            else:
                action = choice.action

            if action == TABLE_ITEM_EXIT:
                break
            elif action == TABLE_ITEM_RETURN:
                break
            elif action == TABLE_ITEM_DEFAULT:
                if callable(self.default_action):
                    try:
                        self.default_action(choice, self.action_dict)
                    except (GetInputInterrupt) as gii:
                        print('\n{}\n'.format(gii))
                        return False
                else:
                    print('Table:run: default_action not set for {}'.format(choice), file=sys.stderr)
            elif callable(action):
                try:
                    action(choice, self.action_dict)
                except (GetInputInterrupt) as gii:
                    print('\n{}\n'.format(gii))
                    continue
            else:
                print('Table.run - no action specified for {}'.format(choice), file=sys.stderr)

            if self.refresh:
                table_choices, table_cleaners, table_convertor, table_validators = self._prep_get_input()
                self.show_rows(self.table.start)

        return True


def create_rows(items, fields, gen_tags=None, item_data=None, add_item_to_item_data=False):
    """
    Create a list of TableItems from an iterable (items) of objects

    :param items: iterable containing items for the table.
    :param List[str] fields: list of field/attribute names to use as column values for each item.
    :param bool gen_tags: if **True** will generate sequentially numbered tags for table items, if False (default) uses
            first column value of each item for the row's tag.
    :param Dict item_data: An optional dictionary to be copied and  attached to the :class:`TableItem` for the row.
    :param bool add_item_to_item_data: if **True** ``item_data['item']`` is set to `item`.

    :return: List[TableItem] of  table items (:class:`TableItem`)

    ``create_rows`` is a convenience function used to create a list of table items (:class:`TableItem`) for a
    ``cooked_input`` :class:`Table`. ``create_rows`` tries to make it easy to create the rows for a table from
    a list of data or a query.

    ``create_rows`` takes an iterable of ``items``, such as a list, dictionary or query. The items in ``items``
    can be just about anything too: objects, lists, dictionaries, tuples, or namedtuples.  ``create_rows`` also
    takes a list of ``fields`` with each item in the list the name of a field or attribute in the items. ``create_rows``
    iterates through ``items`` and add the value for each field as a column value for the table row.

    ``create_rows`` fetches the field data based on the following::

        1. If ``hasattr`` for the fields returns **True** (**__getattr__** is defined), uses ``getattr`` to retreive
            field values. This works nicely for class instances, named tuples, and database query results from an
            object-relationship mapper (ORM).
        2. If the items are dictionaries, uses ``get`` to retreive the value for the key matching the field name.
        3. If both of the previous methods fail, the first len(fields) values of the item are used (requires
            **__get_item__** to be defined.)

    .. note::

        Care is taken to make a single pass through the ``items`` iterable as some iterables are non-reentrant
        (e.g. generators and some database queries)


    Example usage - get a list of integers between 3 and 5 numbers long, separated by colons (:)::

        class Person(object):
            def __init__(self, first, last, age, shoe_size):
                self.first = first
                self.last = last
                self.age = age
                self.shoe_size = shoe_size

        people = [
            Person('John', 'Cleese', 78, 14),
            Person('Terry', 'Gilliam', 77, 10),
            Person('Eric', 'Idle', 75, 12),
        ]

        rows = create_rows(people, ['last', 'first', 'shoe_size'])
        Table(rows, ['First', 'Shoe Size'], tag_str='Last').show_table()

    ``create_rows`` is called by :func:`create_table` to create the table rows.
    """
    tis = []
    GET_ATTR, GET, GET_ITEM = range(3)
    fetch_method = None

    """
    This is a goofy way of doing things, and it would be a lot cleaner to check the types (Iterable, Mapping, etc.) But
    you can't do that in legacy Python (e.g. v2.7) as there is no Typing module. This will be cleaned this up when legacy 
    Python support is dropped.
    """
    if isinstance(items, dict):
        use_items = items.values()
    else:
        use_items = items

    for item in use_items:
        """
        Note: fetch_method is set in the first iteration of the loop as some items are not re-entrant (generators and
        queries from some databases.) If can only use __get_item__ (indexing into a list/array) it assumes the fields
        are in order of the list.
        """
        if item_data is None:
            use_item_data = None
        else:
            use_item_data = dict(item_data)

        if fetch_method is None:    # determine method to fetch items.
            if hasattr(item, fields[0]):
                fetch_method = GET_ATTR
            elif isinstance(item, dict):
                fetch_method = GET
            elif hasattr(item, '__getitem__'):
                fetch_method = GET_ITEM
            else:
                raise RuntimeError('create_rows cannot access data - item needs one of getattr, get, or __getitem__ defined.')

        if fetch_method == GET_ATTR:
            row_data = [ getattr(item, name) for name in fields ]
        elif fetch_method == GET:
            row_data = [ item.get(name) for name in fields ]
        elif fetch_method == GET_ITEM and len(item) >= len(fields):
            row_data = item[:len(fields)]
        else:
            raise RuntimeError(
                'create_rows cannot fetch field values - getattr, get, and __getitem__ all failed.')

        if gen_tags is True:
            tag = None
            use_row_data = row_data
        else:
            tag = row_data[0]
            use_row_data = row_data[1:]

        if add_item_to_item_data is True:
            if use_item_data is None:
                use_item_data = {}
            use_item_data['item'] = item

        tis.append(TableItem(col_values=use_row_data, tag=tag, item_data=use_item_data))

    return tis


def create_table(items, fields, field_names=None, gen_tags=None, item_data=None,
                 add_item_to_item_data=False, title=None, prompt=None, default_choice=None,
                 default_str=None, default_action=TABLE_RETURN_TABLE_ITEM, style=None, **options):
    """
    Convenience function to create ``cooked_input`` a table.

    :param items: iterable containing items for the table.
    :param List[str] fields: list of field/attribute names to use as column values for each item.
    :param List[str] field_names: a list of strings to use for the names of the table columns.
    :param bool gen_tags: if **True** will generate sequentially numbered tags for table items, if False (default) uses
            first column value of each item for the row's tag.
    :param Dict item_data: An optional dictionary to be copied and  attached to the :class:`TableItem` for the row.
    :param bool add_item_to_item_data: if **True** ``item_data['item']`` is set to `item`.
    :param str title: an optional string to use as the title for the table.
    :param str prompt: an optional string to use for the table prompt.
    :param str default_choice: an optional default value to use for when getting input from the table.
    :param str default_str: an optional string to display for the default choice value.
    :param default_action: the default action to take when a table item is picked. Defaults to **TABLE_RETURN_TABLE_ITEM***.
    :param TableStyle style: an optional :class:`TableStyle` to use for the table.
    :param options: a dictionary of optional values for the table. See :class:`Table` for details.

    :return: an instance of a ``cooked_input`` :class:`Table`

    ``create_table`` is a convenience function used to create a ``cooked_input`` table (:class:`Table`) from
    a list of data or a query.

    ``create_table`` calls :func:`create_rows` to create the table rows. See :func:`create_rows` for an explanation
    of the: ``items``, ``fields``, ``gen_tags``, ``item_data``, and ``add_item_to_item_data`` parameters.

    See :class:`Table` for an explanation of the: ``title``, ``prompt``, ``default_choice``, ``default_str``,
        ``default_action``, ``style`` and ``options`` parameters.

    .. note::

        all items are created with the same ``default_action`` and ``item_data`` (with exception of adding the item
        to ``item_data['item']`` if ``add_item_to_item_data`` is **True**.)

    .. note::

        By default all items (rows) are visible and enabled. Rows can be hidden or disabled by setting an
        ``item_filter`` value in the ``options`` dictionary.

    Example usage - get a list of integers between 3 and 5 numbers long, separated by colons (:)::

        items = {
            1: {"episode": 1, "name": "Whither Canada?", "date": "5 October, 1969", "season": 1},
            2: {"episode": 4, "name": "Owl Stretching Time", "date": "26 October, 1969", "season": 1},
            3: {"episode": 15, "name": "The Spanish Inquisition", "date": "22 September, 1970", "season": 2},
            4: {"episode": 35, "name": "The Nude Organist", "date": "14 December, 1972", "season": 2}
        }

        fields = 'episode name date'.split()
        field_names = 'Episode Name Date'.split()
        tbl = create_table(items, fields, field_names, add_item_to_item_data=True, title='Episode List')
        choice = tbl.get_table_choice()
        item = choice.item_data["item"]
        print('{}: {}'.format(item['name'], item['season']))
    """
    use_field_names = None
    new_options = dict(**options)
    if 'tag_str' in options:
        use_tag_str = options['tag_str']
    else:
        use_tag_str = None

    if style is None:
        use_style = TableStyle()
    else:
        use_style = style

    if field_names is None:
        use_field_names = fields

    if gen_tags is True:
        if use_field_names is None:
            use_field_names = field_names

        if use_tag_str is None:
            use_tag_str = ' '
    else:
        if use_field_names is None:
            use_field_names = field_names[1:]
        else:
            use_field_names = use_field_names[1:]

        if use_tag_str is None:
            use_tag_str = field_names[0]

    new_options['tag_str'] = use_tag_str

    tis = create_rows(items, fields, gen_tags, item_data, add_item_to_item_data)
    tbl = Table(tis, col_names=use_field_names, default_choice=default_choice,
                default_str=default_str, default_action=default_action, prompt=prompt, title=title,
                show_cols=use_style.show_cols, show_border=use_style.show_border, style=style, **new_options)
    return tbl


def show_table(table, **options):
    """
    Displays a table without asking for input from the user.

    :param table: a :class:`Table` instance
    :param options: all :class:`Table` options supported, see :class:`Table` documentation for details

    :return: None
    """
    return table.show_table(**options)


def get_table_input(table, **options):
    """
    Get input value from a table of values.

    :param table: a :class:`Table` instance
    :param options: all :class:`Table` options supported, see :class:`Table` documentation for details

    :return: the value from calling :func:`Table.get_table_choice` on the table
    :rtype: Any (dependent on the action function of the :class:`TableItem` selected)
    """
    return table.get_table_choice(**options)


def get_menu(choices, title=None, prompt=None, default_choice=None, add_exit=False, style=None, **options):
    """
    :param choices: the list of text strings to use for the menu items
    :param title: a title to use for the menu
    :param prompt: the prompt string used when asking the user for the menu selection
    :param default_choice: an optional default item to select
    :param add_exit: add an exit item if `True` or not if `False` (default)
    :param style: a :class:`TableStyle` defining the look of the menu.
    :param options: all :class:`Table` options supported, see :class:`Table` documentation for details.

    :return: the result of calling :func:`Table.get_table_choice` on the menu table. Will return the index (one based) of
        the choice selected, unless a different default action is provided in the options. Returns 'exit' if the input
        value is `None` or the menu was exited.
    :rtype: int or str (dependent on default action specified)

    This is a convenience function to create a Table that acts as a simple menu. It takes a list of text strings
    to use for the menu items, and returns the text string of the item picked. `get_menu` is just syntactic sugar
    for calls to the :class:`Table` class, but simpler to use.
    """
    menu_choices = [TableItem(choice) for choice in choices]

    if default_choice is None:
        default_str = None
    else:
        default_str = ' (return for {})'.format(default_choice)

    default_idx = None

    if style is None:
        use_style = TableStyle(show_cols=False, show_border=False, hrules=RULE_NONE, vrules=RULE_NONE)
    else:
        use_style = style

    # return the tag for the menu item unless the user set a specific default action.
    menu_options = dict(**options)

    if 'default_action' not in options:
        menu_options['default_action'] = return_tag_action

    if default_choice is not None:
        for i,mc in enumerate(menu_choices):
            try:
                if mc.tag is not None and mc.tag == default_choice:
                    default_idx = i+1
                elif mc.values[0] == default_choice:
                    default_idx = i+1
                elif mc.tag is None and i == int(default_choice):
                    default_idx = i+1
                break
            except ValueError:
                pass

    menu = Table(menu_choices, title=title, prompt=prompt, default_choice=default_idx, default_str=default_str,
                add_exit=add_exit, style=use_style, **menu_options)
    result = menu.get_table_choice()

    if result is None:
        return 'exit'

    # if add_exit and result.action=='exit':
    if add_exit!="none" and result=='exit':
        return 'exit'

    return result
