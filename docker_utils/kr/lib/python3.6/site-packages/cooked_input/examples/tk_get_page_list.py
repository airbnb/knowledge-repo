"""
Example showing how to use cooked_input for validation of a text input in tkinter. In this example the user is asked
to enter a set of page numbers for a document. The entry is a comma separated list of one or more page numbers (ints)
and page ranges (e.g. "3-7"). The input is returned as a de-duplicated, sorted list of page numbers.

This example shows how to implement a custom convertor (IntervalConvertor) and use process_value to process a
string. It also uses silent_error to silence error reporting.

Len Wanger, 2018
"""

import itertools
from tkinter import Tk, Label, Button, Entry, Text, LEFT, RIGHT, StringVar
import cooked_input as ci

def tk_error_factory(str_var):
    # Factory returns an instance of tk_error with str_var (a tk string variable) as a closure. This allows
    # cooked_input to set error messages in a GUI by setting the string variable.
    def tk_error(fmt_str, value, error_content):
        """
        send errors to a Tk Stringvar.

        :param int fmt_str: a Python `format string <https://docs.python.org/3/library/string.html#formatspec>`_
          for the error. Can use arguments **{value}** and **{error_content}** in the format string
        :param Any value: the value the caused the error
        :param str error_content: additional information for the error

        :return: None
        """
        str_var.set(fmt_str.format(value=value, error_content=error_content))

    return tk_error


class IntervalConvertor(ci.Convertor):
    """
    A cooked_input convertor to convert an integer or a range of integers ("x - y") and return the expanded
    set of integers in a list. Min and max values are used for open ended intervals. If max_val is 12, then
    "10 -" will be converted to [10, 11, 12].

    Note: IntervalConvertor cannot differentiate between negative numbers and an open ended range (i.e. it
        treats '-10' as [min_val: 10]. If negative numbers are needed change the interval designator to another
        character, such as ':'.
    """
    def __init__(self, min_val=None, max_val=None, value_error_str='a number of range of numbers("x - y")'):
        self.min_val = min_val
        self.max_val = max_val
        super(IntervalConvertor, self).__init__(value_error_str)

    def __call__(self, value, error_callback, convertor_fmt_str):
        use_val = value.strip()
        dash_idx = use_val.find('-')

        if dash_idx == -1:
            try:
                return [int(use_val)]
            except (ValueError):
                error_callback(convertor_fmt_str, value, 'an int')
                raise ci.ConvertorError
        else:
            if dash_idx == 0:   # ' - #'
                if self.min_val is None:
                    error_callback(convertor_fmt_str, value, 'an open ended interval')
                    raise ci.ConvertorError
                else:
                    lower_val = use_val[:dash_idx]
                upper_val = use_val[(dash_idx + 1):]
            elif dash_idx == (len(use_val)-1):  # ' # - '
                lower_val = use_val[:dash_idx]
                if self.max_val is None:
                    error_callback(convertor_fmt_str, value, 'an open ended interval')
                    raise ci.ConvertorError
                else:
                    upper_val = use_val[(dash_idx + 1):]
            else:   # '# - #'
                lower_val = use_val[:dash_idx]
                upper_val = use_val[(dash_idx+1):]

        try:
            if len(lower_val) == 0:
                low = self.min_val
            else:
                low = int(lower_val)

            if len(upper_val) == 0:
                high = self.max_val + 1
            else:
                high = int(upper_val) + 1
        except (ValueError):
            error_callback(convertor_fmt_str, value, 'a range of ints ("x - z")')
            raise ci.ConvertorError

        if low > high:
            error_callback(convertor_fmt_str, value, 'a range - the low value is higher than the high value')
            raise ci.ConvertorError

        if high < low:
            error_callback(convertor_fmt_str, value, 'a range - the high value is lower than the low value')
            raise ci.ConvertorError

        return list(range(low, high))


class App(object):
    def __init__(self):
        self.root = Tk()
        self.root.title("Get page numbers test")

        self.max_val_label = Label(self.root, text="Maximum page value")
        self.max_val_label.grid(row=0, column=0)

        self.max_val_var = StringVar()
        self.max_val_var.set('20')
        self.max_val_entry = Entry(self.root, textvariable=self.max_val_var)
        self.max_val_entry.grid(row=0, column=1)

        self.label = Label(self.root, text="Enter the pages to reprint")
        self.label.grid(row=1, column=0)

        self.pages_entry = Entry(self.root)
        self.pages_entry.grid(row=1, column=1)

        self.error_msg_var = StringVar()
        self.tk_error = tk_error_factory(self.error_msg_var)
        self.error_msg_var.set('')
        self.error_msg = Label(self.root, textvariable=self.error_msg_var)
        self.error_msg.grid(row=2, column=0)

        self.ok_button = Button(self.root, text="Ok", command=self.process_entry)
        self.ok_button.grid(row=4, column=1)

    def process_entry(self):
        max_val = int(self.max_val_var.get())
        page_entry_val = self.pages_entry.get()
        interval_gi = ci.GetInput(convertor=IntervalConvertor(min_val=1, max_val=max_val), error_callback=self.tk_error)
        list_gi = ci.GetInput(convertor=ci.ListConvertor(interval_gi),
                  validators=ci.ListValidator(len_validators=ci.RangeValidator(min_val=1)), error_callback=self.tk_error)
        valid, result = list_gi.process_value(page_entry_val)

        if valid is True:
            page_list = sorted(set(itertools.chain.from_iterable(result)))
            print(f'page_list={page_list}')
            self.root.destroy()


app = App()
app.root.mainloop()