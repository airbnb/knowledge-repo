
"""
pytest tests for cooked_input -- test convertor functions


Len Wanger, 2017
"""

import sys

if sys.version_info[0] > 2:  # For Python 3
    from io import StringIO
else:
    from StringIO import StringIO

from cooked_input import get_input, get_boolean, get_list, get_date, get_yes_no
from cooked_input import Convertor, IntConvertor, BooleanConvertor, ListConvertor, DateConvertor, YesNoConvertor
from cooked_input import StripCleaner
from .utils import redirect_stdin


class TestConvertors(object):
    bool_convertor = BooleanConvertor()

    def test_base_class(self):
        c = Convertor('')
        c('foo', None, None) # for coverage testing only!

    def test_get_boolean_true(self):
        input_str = u"""
            10
            
            true
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='enter a boolean (True/False)', cleaners=StripCleaner(), convertor=self.bool_convertor)
            print(result)
            assert(result==True)

        print(self.bool_convertor)   # for code coverage

    def test_get_boolean_false(self):
        input_str = u"""
            10

            f
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_input(prompt='enter a boolean (True/False)', cleaners=StripCleaner(), convertor=self.bool_convertor)
            print(result)
            assert (result == False)


    def test_get_bool(self):
        input_str = u"""
            no
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_boolean()
            print(result)
            assert (result == False)


    def test_get_list(self):
        input_str = u"""
            foo, bar, blat
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_list()
            print(result)
            assert (result == ['foo', 'bar', 'blat'])


    def test_get_input_list(self):
        input_str = u"""
            foo, bar, blat
            """

        lc = ListConvertor()
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=lc)
            print(result)
            assert (result == ['foo', 'bar', 'blat'])

        print(lc)   # for code coverage


    def test_get_date(self):
        input_str = u"""
            foo
            9/4/2017
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_date()
            print(result)
            assert (str(result) == '2017-09-04 00:00:00')

    def test_get_input_date(self):
        input_str = u"""
            9/4/2017
            """

        dc = DateConvertor()
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=dc)
            print(result)
            assert (str(result) == '2017-09-04 00:00:00')

        print(dc)   # for code coverage


    def test_get_yes_no(self):
        input_str = u"""
            foo
            Yes
            """

        with redirect_stdin(StringIO(input_str)):
            result = get_yes_no()
            print(result)
            assert (result == 'yes')

    def test_get_input_yes_no(self):
        input_str = u"""
            foo
            No
            """

        ync = YesNoConvertor()
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=ync)
            print(result)
            assert (result == 'no')
        print(ync)