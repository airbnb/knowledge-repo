
"""
pytest tests for cooked_input: test the utility functions

Len Wanger, 2017
"""

import pytest

from cooked_input.input_utils import compose, put_in_a_list
from cooked_input.input_utils import swap_element, renumerate, cap_last_word

class TestUtils(object):

    def a(self, value):
        return value + 1

    def b(self, value):
        return value * 2

    def c(self, value):
        return str('result is: {}'.format(value))

    def test_compose(self):
        # test compose function
        result = compose(4, funcs=[self.a, self.b, self.c])
        assert(result == 'result is: 10')

    def test_put_in_a_list(self):
        # test put_in_a_list function
        result = put_in_a_list(None)
        assert(result == [])

        result = put_in_a_list(10)
        assert (result == [10])

        t = (10, 20, 30)
        result = put_in_a_list(t)
        print(result)
        assert (result == [10, 20, 30])

        result = put_in_a_list((10, 20))
        assert (result == [10, 20])

        result = put_in_a_list('foo')
        assert (result == ['foo'])

        result = put_in_a_list(['foo', 'bar'])
        assert (result == ['foo', 'bar'])

        t = tuple('abc')
        result = put_in_a_list(t)
        print(result)
        assert (result == ['a', 'b', 'c'])

    def test_renumerate(self):
        values = reversed(list(enumerate('bar')))
        for i,v in renumerate('bar'):
            assert(next(values)==(i,v))

        values = reversed(list(enumerate([10, 20, 30])))
        for i, v in renumerate([10, 20, 30]):
            assert (next(values) == (i, v))

    def test_swap_element(self):
        values = [
            ('foo', 0, 'F'),
            ('foo', 1, 'O'),
            ('foo', 2, 'O'),
            ('foo', -3, 'F'),
            ('foo', -2, 'O'),
            ('foo', -1, 'O'),
            ('f', 0, 'F'),
            ('f', -1, 'F'),
        ]
        print("\nswap_element:\n")
        for v in values:
            result = swap_element(v[0], v[1], v[2])

        values = [
            ('foo', 4, 'O'),  # IndexError
            ('foo', -4, 'O'),  # IndexError
        ]
        for v in values:
            with pytest.raises(IndexError):
                swap_element(v[0], v[1], v[2])

        values = [
            ('', 0, 'F'),  # ValueError
        ]
        for v in values:
            with pytest.raises(ValueError):
                swap_element(v[0], v[1], v[2])

    def test_cap_last_word(self):
        values = [
            ('foo', 'Foo'),
            ('foo bar', 'foo Bar'),
            ('   \t ', '   \t '),
        ]

        for value in values:
            result = cap_last_word(value[0])
            assert(result == value[1])
