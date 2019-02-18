
"""
Example showing how to use cooked_input to validate form data from a GUI. In this case tkinter.

Len Wanger, 2017
"""

import sys

if sys.version_info[0] > 2: # For Python 3
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter import messagebox
else: # For Python 2
    import Tkinter as tk
    import Tkinter.ttk as ttk
    from Tkinter import tkMessageBox as messagebox

from cooked_input import process_value, IntConvertor, RangeValidator, StripCleaner


def tk_msg_box_error(fmt_str, value, error_content):
    # display the error in a message box
    messagebox.showerror('Entry not valid', fmt_str.format(value=value, error_content=error_content))


def on_button():
    value = entry1.get()
    valid, processed_value = process_value(value, cleaners=StripCleaner(), convertor=IntConvertor(),
                                     validators=RangeValidator(min_val=1, max_val=10), error_callback=tk_msg_box_error)

    if valid:
        messagebox.showinfo("Integer is...", "Integer is good: {}".format(processed_value))
        top.quit()



if __name__ == '__main__':
    top = tk.Tk()
    top.title('Cooked Input Example')

    main = ttk.Frame(top, padding=' 3 12 12')
    main.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    main.columnconfigure(0, weight=1)
    main.rowconfigure(0, weight=1)

    label1 = tk.Label(main, text='integer (between 1 and 10)')
    entry1 = tk.Entry(main)
    btn = tk.Button(main, text='OK', command=on_button)

    label1.grid(column=1, row=1, sticky=(tk.W, tk.E))
    entry1.grid(column=2, row=1, sticky=(tk.W, tk.E))
    btn.grid(column=2, row=2, sticky=(tk.W, tk.E))

    top.mainloop()

