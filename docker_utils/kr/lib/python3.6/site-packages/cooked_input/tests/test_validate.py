
"""
pytest tests for cooked_input: test the validate method

Len Wanger, 2017
"""

import pytest
import sys

if sys.version_info[0] > 2:  # For Python 3
    from io import StringIO
else:
    from StringIO import StringIO

from cooked_input import validate, Validator, RangeValidator, NoneOfValidator
from cooked_input import GetInput, get_input, print_error, StripCleaner, IntConvertor, ListConvertor, AnyOfValidator
from cooked_input import NoneOfValidator, LengthValidator
from cooked_input import EqualToValidator, ListValidator, PasswordValidator, ChoiceValidator, SimpleValidator, RegexValidator

from .utils import redirect_stdin


class TestValidate(object):

    def test_validate(self):
        result = validate(3, validators=RangeValidator(min_val=1, max_val=10))
        assert (result == 1)

        validators = [RangeValidator(min_val=1, max_val=10), NoneOfValidator(5)]

        for v in [(-1, False), (1, True), (5, False), (6, True), (11, False)]:
            result = validate(v[0], validators)
            assert(result==v[1])

    def test_bad_type(self):
        # For specific test coverage cases to catch no __ge__ specified on type
        class A(object):
            a=1

        result = validate(A(), RangeValidator(min_val=1, max_val=None))
        result = validate(A(), RangeValidator(min_val=None, max_val=10))

    def test_call_abstract(self):
        v = Validator()
        v(10, None, None)


    def test_any_of(self):
        input_str = u"""
            -1
            6
            16
            2
            """

        av = AnyOfValidator(validators=[RangeValidator(0,5), RangeValidator(10,15)])
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=av)
            print(result)
            assert (result == 2)

        print(av)   # for code coverage

        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=None)
            print(result)
            assert (result == -1)

        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=RangeValidator(5,10))
            print(result)
            assert (result == 6)

        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=16)
            print(result)
            assert (result == 16)

        av = AnyOfValidator(validators=EqualToValidator(16))
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=av)
            print(result)
            assert (result == 16)

        av = AnyOfValidator(validators=16)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=av)
            print(result)
            assert (result == 16)

        av = AnyOfValidator(validators=None)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=av)
            print(result)
            assert (result == -1)


    def test_none_of(self):
        input_str = u"""
            -1
            6
            16
            2
            """

        nov = NoneOfValidator(validators=[RangeValidator(0,5), RangeValidator(10,15)])
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=nov)
            print(result)
            assert (result == -1)

        print(nov)   # for code coverage

        nov = NoneOfValidator(validators=RangeValidator(-2,5))
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=nov)
            print(result)
            assert (result == 6)



    def test_length(self):
        input_str = u"""
            1
            foo
            foobar
            foob
            fb
            """

        lv = LengthValidator()
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), validators=lv)
            print(result)
            assert (result == '1')

        print(lv)   # for code coverage

        lv = LengthValidator(min_len=2)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), validators=lv)
            print(result)
            assert (result == 'foo')

        lv = LengthValidator(max_len=2)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), validators=lv)
            print(result)
            assert (result == '1')

        lv = LengthValidator(min_len=4, max_len=5)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), validators=lv)
            print(result)
            assert (result == 'foob')


    def test_equal(self):
        input_str = u"""
            1
            3
            """

        ev = EqualToValidator(3)
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=IntConvertor(), validators=ev)
            print(result)
            assert (result == 3)

        print(ev)   # for code coverage


    def test_list(self):
        input_str = u"""
            1
            3,4,5,6,7
            2,3,4
            """

        lc = ListConvertor(elem_get_input=GetInput(convertor=IntConvertor()))
        lv = ListValidator(len_validators=RangeValidator(min_val=2, max_val=7))
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=lc, validators=lv)
            print(result)
            assert (result == [3,4,5,6,7])

        print(lv)   # for code coverage

        lv = ListValidator(len_validators=RangeValidator(min_val=2), elem_validators=RangeValidator(max_val=6))
        with redirect_stdin(StringIO(input_str)):
            result = get_input(cleaners=StripCleaner(), convertor=lc, validators=lv)
            print(result)
            assert (result == [2,3,4])

    def test_password(self):
        input_str = "\nfoo\nfooFFFF\nffffffffoooooobbbb\nFOOBAR!\nfoobar!\nFooBar!\nFooBar1!\nFooBar1!!\nfbr^"
        any_password_val = PasswordValidator()

        with redirect_stdin(StringIO(input_str)):
            result = get_input(validators=any_password_val)
            print(result)
            assert (result == 'foo')

        print(any_password_val)  # for code coverage

        with redirect_stdin(StringIO(input_str)):
            result = get_input(validators=[any_password_val], prompt='type in any password', required=False, hidden=True)
            print(result)
            assert (result is None)

        stronger_password_val = PasswordValidator(allowed='fobarFOB1!^', disallowed='[]', min_len=5, max_len=15, min_lower=4, min_upper=2, min_digits=1, min_puncts=2)

        with redirect_stdin(StringIO(input_str)):
            result = get_input(validators=[stronger_password_val],
                               prompt='type in a password (length=5-15, with at least 2 lower, 2 upper, 1 digit, and 2 puncts)', hidden=True)
            print(result)
            assert (result == 'FooBar1!!')

        disallowed_chars = 'aeiou!*&%2468'
        disallowed_chars_password_val = PasswordValidator(disallowed=disallowed_chars)

        with redirect_stdin(StringIO(input_str)):
            result = get_input(validators=[disallowed_chars_password_val], prompt='type in a password (type in a password(no vowels, even digits or !, *, \ %)')
            print(result)
            assert (result == 'fbr^')

    def test_password_coverage(self):
        # Call PasswordValidator directly with the wrong value type to get to error conditions in coverage testing
        pv = PasswordValidator()
        pv(10, print_error, "{value}")

    def test_choices(self):
        input_str = "\nfoo\nffffffffoooooobbbb\nFOOBAR!\nfoobar!\nFooBar!\nfoobar\nFooBar1!\nFooBar1!!\nfbr^"
        cv = ChoiceValidator(choices=['foobar', 'bar', 'blat'])

        with redirect_stdin(StringIO(input_str)):
            result = get_input(validators=cv)
            print(result)
            assert (result == 'foobar')

        print(cv)  # for code coverage

    def test_simple(self):
        def simple_func(value):
            return True if value == 'foobar' else False

        input_str = "\nfoo\nffffffffoooooobbbb\nFOOBAR!\nfoobar!\nFooBar!\nfoobar\nFooBar1!\nFooBar1!!\nfbr^"
        sv = SimpleValidator(validator_func=simple_func, name='simple validator')

        with redirect_stdin(StringIO(input_str)):
            result = get_input(validators=sv)
            print(result)
            assert (result == 'foobar')

        print(sv)  # for code coverage

        sv = SimpleValidator(validator_func=simple_func, name='bad option')


    def test_regex(self):
        input_str = "\n1234\n2345678901"
        rev = RegexValidator(pattern=r'^[2-9]\d{9}$', regex_desc='a 10 digit phone number')

        with redirect_stdin(StringIO(input_str)):
            result = get_input(validators=rev)
            print(result)
            assert (result == '2345678901')

        print(rev)  # for code coverage

        rev = RegexValidator(pattern=r'^[2-9]\d{9}$')

        with redirect_stdin(StringIO(input_str)):
            result = get_input(validators=rev)
            print(result)
            assert (result == '2345678901')

        with pytest.raises(EOFError):
            with redirect_stdin(StringIO(input_str)):
                result = get_input(convertor=IntConvertor(), validators=rev)

        rev = RegexValidator(pattern=r'^[2-9]\d{9}$', regex_desc='bad option')

