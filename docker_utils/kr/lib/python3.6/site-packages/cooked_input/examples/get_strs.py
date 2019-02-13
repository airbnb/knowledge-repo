"""
cooked input examples of getting an string values

Len Wanger, 2017
"""

from cooked_input import get_input, get_string
from cooked_input.validators import LengthValidator, ChoiceValidator, NoneOfValidator
from cooked_input.cleaners import StripCleaner, CapitalizationCleaner
from cooked_input.convertors import YesNoConvertor

if __name__ == '__main__':
    colors = ['red', 'green', 'blue']
    good_flavors = ['cherry', 'lime', 'lemon', 'orange']
    bad_flavors = 'licorice'

    good_flavor_validator = ChoiceValidator(choices=good_flavors)
    not_in_choices_validator = NoneOfValidator(validators=[ChoiceValidator(choices=bad_flavors)])
    strip_and_lower_cleaners = [StripCleaner(), CapitalizationCleaner(style='lower')]


    # simplest way
    print(get_string(prompt='Enter some text'))

    # strip and capitalization cleaners
    print(get_input(prompt='Enter any string (will be stripped of trailing spaces and converted to upper)',
                    cleaners=[StripCleaner(lstrip=False, rstrip=True), CapitalizationCleaner(style='upper')]))

    print(get_input(prompt='Enter your name (all words will be capitalized)', cleaners=CapitalizationCleaner(style='all_words')))

    # picking from choices (InchoicesValidator)
    prompt_str = "What is your favorite flavor jelly bean (pick any flavor, don't say licorice!)?"
    print(get_input(prompt=prompt_str, validators=not_in_choices_validator, default='cherry'))

    prompt_str = "Which of these is your favorite flavor jelly bean (choose from: %s, but not licorice!)?" % ', '.join(good_flavors)
    validators = [good_flavor_validator, not_in_choices_validator]
    print(get_input(prompt=prompt_str, cleaners=strip_and_lower_cleaners, validators=validators, default='cherry'))

    # specifying string length
    print(get_input(prompt='Enter a 2 to 4 letter string', validators=[LengthValidator(min_len=2, max_len=4)]))

    # Use YesNoConvertor
    print(get_input(prompt="Yes or no?", cleaners=StripCleaner(), convertor=YesNoConvertor(), default='Y'))
