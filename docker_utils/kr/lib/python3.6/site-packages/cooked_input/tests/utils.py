
"""
pytest test utilities for cooked_input

Len Wanger, 2017
"""

import sys

if sys.version_info[0] > 2:  # For Python 3
    from io import StringIO
else:
    from StringIO import StringIO


from cooked_input import get_input, IntConvertor, RangeValidator


class redirect_stdin():
    # context manager for redirecting stdin. Usable with "with" keyword
    def __init__(self, f):
        self.f = f

    def __enter__(self):
        sys.stdin = self.f

    def __exit__(self, *args):
        sys.stdin = sys.__stdin__
