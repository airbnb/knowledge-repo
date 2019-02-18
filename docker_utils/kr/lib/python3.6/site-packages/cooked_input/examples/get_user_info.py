"""
cooked input examples of getting inputs from tables

Len Wanger, 2017
"""


"""
Example of using cooked_input to get user login information. This example shows several features of 
cooked_input:

- Dealing with hidden inputs, retries, passwords, validating with validus, and writing custom validators.

First, it gets the login and password from the user, then it updates the user's profile information.

Warning: This is a simple example and does not represent what you would do in a secure environment. For
simplicity I have hard-coded a list of users with passwords hashed with the Python hash function. In
practice a call would be made to check the user name with the operating system. For instance, on Unix
systems the Python pwd module (part of the standard library) can be used:

    import pwd
    user_info = pwd.getpwnam(username)

The structure returned has the user ID and the encrypted passwd. To check the password, you encrypt the plain
text password and check it against the encrypted password. Something like this (on Unix systems):

    import pwd
    import crypt
    import getpass
    from hmac import compare_digest as compare_hash

    def compare_passwords(username, plaintext):
        stored_hash = pwd.getpwnam(username)[1]
        plaintext_hashed = crypt.crypt(plaintext)
        if compare_hash(plaintext_hashed, stored_hash):
            return True
        else:
            return False

Len Wanger, 2017
"""

import sys
from validus import isemail

from cooked_input import get_input
from cooked_input.cleaners import StripCleaner, CapitalizationCleaner
from cooked_input.convertors import ListConvertor
from cooked_input.validators import Validator, PasswordValidator, ListValidator, ChoiceValidator, EqualToValidator
from cooked_input.validators import SimpleValidator


class CheckUserValidator(Validator):
    """
    This is a custom validator to check if a user is valid. For simplicity in this example I have
    hard-coded valid user names. In practice a call would be made to check the user name with the
    operating system. For instance, on Unix systems the Python pwd module (part of the standard library)
    can be used. See more details above.
    """
    def __init__(self):
        pass

    def __call__(self, value, error_callback, validator_fmt_str):
        if value in user_list:
            return True
        else:
            valid_users = [ k for k in user_list.keys() ]
            error_callback(validator_fmt_str, value, 'not in list of users ({})'.format(valid_users))
            return False


class CheckPasswordValidator(Validator):
    """
    This is a custom validator to check whether the password matches the encrypted password for the user. For simplicity
    this in this example, I have hard-coded user information with passwords hashed with the Python hash function. In
    practice this is a very bad idea. See above for more details.

    """
    def __init__(self, username):
        self.username = username

    def __call__(self, value, error_callback, validator_fmt_str):
        hashed_value = hash(value)
        is_match = user_list[self.username]['password'] == hashed_value

        if is_match:
            return True
        else:
            error_callback(validator_fmt_str, 'entered password', 'does not match current password'.format())
            return False


if __name__ == '__main__':
    # The BBC would like to appologize for this fake list of users. passwords are encrypted with the Python hash function for simplicity. See warnings above!
    user_list = {
        'gc': {'first_name': 'Graham', 'last_name': 'Chapman', 'email': 'king.arthur@camelot.com', 'password': hash('IWasBrian2!'), 'roles': ['admin', 'arthur'] },
        'jc': {'first_name': 'John', 'last_name': 'Cleese', 'email': 'basel@fawlty-towers.com', 'password': hash('&Now4SomethingCompletelyDifferent...'), 'roles': ['praline']},
        'tg': {'first_name': 'Terry', 'last_name': 'Gilliam', 'email': 'director@movie.com.br', 'password': hash('Its-Spelled-Color'), 'roles': ['animator']},
        'tj': {'first_name': 'Terry', 'last_name': 'Jones', 'email': 'erik@drag.com.np', 'password': hash('Hes_1_very_naughty_boy'), 'roles': ['mandy']},
        'mp': {'first_name': 'Michael', 'last_name': 'Palin', 'email': 'south_pole@pbs.org', 'password': hash('Face*2*Face'), 'roles': ['anchovy', 'travel-guide']},
        'ei': {'first_name': 'Eric', 'last_name': 'Idle', 'email': 'nudge@nudge.com', 'password': hash('1/2aB'), 'roles': ['arthur', 'timmy', 'stig']},
    }

    # Fake list of allowed roles
    roles_list = ['admin', 'arthur', 'praline', 'mandy', 'animator', 'anchovy', 'stig', 'timmy', 'travel-guide']

    strip_cleaner = StripCleaner()
    default_cleaners = [StripCleaner(), CapitalizationCleaner(style='lower')]
    name_cleaners = [StripCleaner(), CapitalizationCleaner(style='all_words')]
    strong_password_validator = PasswordValidator(disallowed='[]', min_len=5, max_len=15, min_lower=2, min_puncts=2)
    email_validator = SimpleValidator(isemail, name='email')    # validator from validus function
    role_validator = ListValidator(elem_validators=ChoiceValidator(roles_list))
    role_prompt = 'Roles ({}, separated by commas)'.format(sorted(roles_list))
    password_confirm_fmt_str = 'password does not match'

    # Give a hint to new users...
    print('\n\nThis is an example of using cooked_input to simulate getting login information for a user.')
    print('\nFor test purposes, you can log in as user: gc with password: IWasBrian2!\n')
    print('\nFor more examples look at the source code\n\n')

    # Simulate logging the user in:
    try:
        user_name = get_input(prompt='Username', cleaners=default_cleaners, validators=CheckUserValidator(), retries=3)
        password = get_input(prompt='Password', cleaners=None, validators=CheckPasswordValidator(user_name), hidden=True, retries=3)
    except RuntimeError:
        print('Maximum retries exceeded.... exiting')
        sys.exit(1)

    # Get updated profile information for the user:
    old_data = user_list[user_name]
    password = get_input(prompt='Enter new Password', cleaners=None, validators=strong_password_validator, hidden=True)

    try:
        password = get_input(prompt='Confirm new Password', cleaners=None, validators=EqualToValidator(password),
                             hidden=True, retries=3, validator_error_fmt=password_confirm_fmt_str)
    except RuntimeError:
        print('Maximum retries exceeded.... exiting')
        sys.exit(1)

    first_name = get_input(prompt='First name', cleaners=name_cleaners, default=old_data['first_name'])
    last_name = get_input(prompt='Last name', cleaners=name_cleaners, default=old_data['last_name'])
    email_err_fmt_str = '"{value}" is not a valid email address'
    email = get_input(prompt='Email', cleaners=default_cleaners, validators=email_validator,
                        validator_error_fmt=email_err_fmt_str, default=old_data['email'])
    roles = get_input(prompt=role_prompt, cleaners=default_cleaners, convertor=ListConvertor(), validators=role_validator, default=', '.join(old_data['roles']))

    print('\nUpdated user profile info: user_name: {}, password: {}, first_name: {}, last_name: {}, email: {}, roles: {}'.format(
        user_name, password, first_name, last_name, email, roles))
