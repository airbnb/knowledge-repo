"""
cooked input examples of the choice, replace and (&?) regex cleaners

Len Wanger, 2017
"""

import re
from cooked_input import get_input
from cooked_input.cleaners import ChoiceCleaner, ReplaceCleaner, RegexCleaner
from cooked_input.validators import ChoiceValidator


if __name__ == '__main__':
    # ChoiceCleaner examples:
    color_choices = ['Black', 'Brown', 'BLUE', 'red', 'green']
    color_choice_cleaner = ChoiceCleaner(color_choices)

    color_choice_cleaner_case_insensitive = ChoiceCleaner(color_choices, case_sensitive=False)

    color_choice_validator = ChoiceValidator(color_choices)
    float_choice_cleaner = ChoiceCleaner(choices=[1.0, 10.0, 1.11, 3.141569])

    print(get_input(prompt='Enter a color (choices: {})'.format(', '.join(color_choices)),
                    cleaners=color_choice_cleaner, validators=color_choice_validator))
    print(get_input(prompt='Enter a color (choices: {} - case insensitive)'.format(', '.join(color_choices)),
                    cleaners=[color_choice_cleaner_case_insensitive], validators=color_choice_validator))
    print(get_input(prompt='Enter a number (choices: [1.0], [10].0, [1.1]1, [3].141569)', cleaners=float_choice_cleaner))

    # ReplaceCleaner examples:
    replace_color = ReplaceCleaner(old='color', new='colour')
    replace_color_twice = ReplaceCleaner(old='color', new='colour', count=2)
    replace_pi = ReplaceCleaner(old='Pi', new="3.141569")

    print(get_input(prompt='Enter any string ("color" replaced by "colour")', cleaners=replace_color))
    print(get_input(prompt='Enter any string ("color" replaced by "colour, max 2 times")', cleaners=replace_color_twice))
    # print(get_input(prompt='Enter any string ("trash" replaced by "rubbish")', cleaners=replace_trash))
    print(get_input(prompt='Enter any string ("Pi" replaced by its float value)', cleaners=replace_pi))

    # RegexCleaner examples:
    regex_and = RegexCleaner(pattern=r'\sAND\s', repl=' & ', flags=re.IGNORECASE)
    regex_period = RegexCleaner(pattern=r'\.', repl='. Nudge nudge. Know what I mean... say no more.', flags=re.IGNORECASE)

    print(get_input(prompt='Enter any string ("and" replaced with "&")', cleaners=regex_and))
    print(get_input(prompt='Enter any string ("." replaced with something completely different)', cleaners=regex_period))

    # compose them all together
    print(get_input(prompt='Enter any string (all five cleaners applied)', cleaners=[color_choice_cleaner, replace_color,
                    replace_pi, regex_and, regex_period]))


