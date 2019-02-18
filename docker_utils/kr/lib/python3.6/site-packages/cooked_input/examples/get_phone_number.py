
"""
An example of getting a phone number.

This example propmpts the user for a a phone number, without making them jump through hoops to format it!

    - Make sure it's 10 digits
    - Strip out any '(', ')', '-', or spaces.
    - Return as a string

This example shows the RemoveCleaner to strip out unwanted characters and the RegexCleaner to check
the phone number has 10 digits and doesn't start with '0' or '1'.

A more sophisticated phone validator comes with validus (see: [https://shopnilsazal.github.io/validus/usage.html?highlight=phone#validus.isphone])

Len Wanger, 2017
"""

from cooked_input import get_input, RegexValidator
from cooked_input import StripCleaner, RemoveCleaner, RegexCleaner

if __name__ == '__main__':
    phone_validator = [RegexValidator(pattern=r'^[2-9]\d{9}$', regex_desc='a 10 digit phone number')]
    remove_cleaners = [StripCleaner(), RemoveCleaner(patterns=list('()-, ')), RegexCleaner(pattern=r'^[01]', repl=r'')]

    print('Get a phone number from the user. You can format it anyway you want (spaces, dashes, parenthesis, and leading 0 or 1 stripped out)')
    result = get_input(cleaners=remove_cleaners, validators=phone_validator, prompt='Please enter a phone number')
    print(result)
