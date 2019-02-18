"""
cooked input examples of getting password values

Len Wanger, 2017
"""

from cooked_input import get_input
from cooked_input.validators import PasswordValidator


if __name__ == '__main__':
    any_password_val = PasswordValidator()
    stronger_password_val = PasswordValidator(disallowed='[]', min_len=5, max_len=15, min_lower=2, min_upper=2, min_digits=1, min_puncts=2)
    disallowed_chars = 'aeiou!*&%2468'
    disallowed_chars_password_val = PasswordValidator(disallowed=disallowed_chars)

    result = get_input(cleaners=None, convertor=None, validators=[any_password_val], prompt='type in any password', required=False, hidden=True)
    print('password result=%r' % (result))

    result = get_input(cleaners=None, convertor=None, validators=[stronger_password_val], prompt='type in a password (length=5-15, with at least 2 lower, 2 upper, 1 digit, and 2 puncts)',
                       required=False, hidden=True)
    print('password result=%r' % (result))

    result = get_input(cleaners=None, convertor=None, validators=[disallowed_chars_password_val],
                       prompt='type in a password (no vowels, even digits or !, *, \ %)',
                       required=False, hidden=True)
    print('password result=%r' % (result))
