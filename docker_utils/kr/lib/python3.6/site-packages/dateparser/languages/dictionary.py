# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain
from operator import methodcaller
import regex as re
from six.moves import zip_longest

from dateparser.utils import normalize_unicode

PARSER_HARDCODED_TOKENS = [":", ".", " ", "-", "/"]
PARSER_KNOWN_TOKENS = ["am", "pm", "UTC", "GMT", "Z"]
ALWAYS_KEEP_TOKENS = ["+"] + PARSER_HARDCODED_TOKENS
KNOWN_WORD_TOKENS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                     'saturday', 'sunday', 'january', 'february', 'march',
                     'april', 'may', 'june', 'july', 'august', 'september',
                     'october', 'november', 'december', 'year', 'month', 'week',
                     'day', 'hour', 'minute', 'second', 'ago', 'in', 'am', 'pm']

PARENTHESES_PATTERN = re.compile(r'[\(\)]')
NUMERAL_PATTERN = re.compile(r'(\d+)')


class UnknownTokenError(Exception):
    pass


class Dictionary(object):
    """
    Class that modifies and stores translations and handles splitting of date string.

    :param locale_info:
        Locale info (translation data) of the locale.
    :type language_info: dict

    :param settings:
        Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
    :type settings: dict

    :return: a Dictionary instance.
    """

    _split_regex_cache = {}
    _sorted_words_cache = {}
    _split_relative_regex_cache = {}
    _sorted_relative_strings_cache = {}
    _match_relative_regex_cache = {}

    def __init__(self, locale_info, settings=None):
        dictionary = {}
        self._settings = settings
        self.info = locale_info

        if 'skip' in locale_info:
            skip = map(methodcaller('lower'), locale_info['skip'])
            dictionary.update(zip_longest(skip, [], fillvalue=None))
        if 'pertain' in locale_info:
            pertain = map(methodcaller('lower'), locale_info['pertain'])
            dictionary.update(zip_longest(pertain, [], fillvalue=None))
        for word in KNOWN_WORD_TOKENS:
            if word in locale_info:
                translations = map(methodcaller('lower'), locale_info[word])
                dictionary.update(zip_longest(translations, [], fillvalue=word))
        dictionary.update(zip_longest(ALWAYS_KEEP_TOKENS, ALWAYS_KEEP_TOKENS))
        dictionary.update(zip_longest(map(methodcaller('lower'),
                                          PARSER_KNOWN_TOKENS),
                                          PARSER_KNOWN_TOKENS))

        relative_type = locale_info.get('relative-type', {})
        for key, value in relative_type.items():
            relative_translations = map(methodcaller('lower'), value)
            dictionary.update(zip_longest(relative_translations, [], fillvalue=key))

        self._dictionary = dictionary

        no_word_spacing = locale_info.get('no_word_spacing', 'False')
        self._no_word_spacing = bool(eval(no_word_spacing))

        relative_type_regex = locale_info.get("relative-type-regex", {})
        self._relative_strings = list(chain(*relative_type_regex.values()))

    def __contains__(self, key):
        if key in self._settings.SKIP_TOKENS:
            return True
        return self._dictionary.__contains__(key)

    def __getitem__(self, key):
        if key in self._settings.SKIP_TOKENS:
            return None
        return self._dictionary.__getitem__(key)

    def __iter__(self):
        return chain(self._settings.SKIP_TOKENS, iter(self._dictionary))

    def are_tokens_valid(self, tokens):
        """
        Check if tokens are valid tokens for the locale.

        :param tokens:
            a list of string or unicode tokens.
        :type tokens: list

        :return: True if tokens are valid, False otherwise.
        """
        match_relative_regex = self._get_match_relative_regex_cache()
        for token in tokens:
            if any([match_relative_regex.match(token),
                    token in self, token.isdigit()]):
                continue
            else:
                return False
        else:
            return True

    def split(self, string, keep_formatting=False):
        """
        Split the date string using translations in locale info.

        :param string:
            Date string to be splitted.
        :type string:
            str|unicode

        :param keep_formatting:
            If True, retain formatting of the date string.
        :type keep_formatting: bool

        :return: A list of string tokens formed after splitting the date string.
        """
        if not string:
            return string

        split_relative_regex = self._get_split_relative_regex_cache()
        match_relative_regex = self._get_match_relative_regex_cache()

        tokens = split_relative_regex.split(string)

        for i, token in enumerate(tokens):
            if match_relative_regex.match(token):
                tokens[i] = [token]
                continue
            tokens[i] = self._split_by_known_words(token, keep_formatting)

        return list(filter(bool, chain(*tokens)))

    def _split_by_known_words(self, string, keep_formatting):
        if not string:
            return string

        regex = self._get_split_regex_cache()
        match = regex.match(string)
        if not match:
            return (self._split_by_numerals(string, keep_formatting)
                    if self._should_capture(string, keep_formatting) else [])

        unparsed, known, unknown = match.groups()
        splitted = [known] if self._should_capture(known, keep_formatting) else []
        if unparsed and self._should_capture(unparsed, keep_formatting):
            splitted = self._split_by_numerals(unparsed, keep_formatting) + splitted
        if unknown:
            splitted.extend(self._split_by_known_words(unknown, keep_formatting))

        return splitted

    def _split_by_numerals(self, string, keep_formatting):
        return [token for token in NUMERAL_PATTERN.split(string)
                if self._should_capture(token, keep_formatting)]

    def _should_capture(self, token, keep_formatting):
        return (
            keep_formatting or
            (token in ALWAYS_KEEP_TOKENS) or
            re.match(r"^.*[^\W_].*$", token, re.U)
        )

    def _get_sorted_words_from_cache(self):
        if (
                self._settings.registry_key not in self._sorted_words_cache or
                self.info['name'] not in self._sorted_words_cache[self._settings.registry_key]
           ):
            self._sorted_words_cache[self._settings.registry_key] = {
                self.info['name']: sorted([key for key in self], key=len, reverse=True)
            }
        return self._sorted_words_cache[self._settings.registry_key][self.info['name']]

    def _get_split_regex_cache(self):
        if (
                self._settings.registry_key not in self._split_regex_cache or
                self.info['name'] not in self._split_regex_cache[self._settings.registry_key]
           ):
            self._construct_split_regex()
        return self._split_regex_cache[self._settings.registry_key][self.info['name']]

    def _construct_split_regex(self):
        known_words_group = "|".join(map(re.escape, self._get_sorted_words_from_cache()))
        if self._no_word_spacing:
            regex = r"^(.*?)({})(.*)$".format(known_words_group)
        else:
            regex = r"^(.*?(?:\A|\W|_|\d))({})((?:\Z|\W|_|\d).*)$".format(known_words_group)
        self._split_regex_cache[self._settings.registry_key] = {
            self.info['name']: re.compile(regex, re.UNICODE | re.IGNORECASE)
        }

    def _get_sorted_relative_strings_from_cache(self):
        if (
            self._settings.registry_key not in self._sorted_relative_strings_cache or
            self.info['name'] not in self._sorted_relative_strings_cache[self._settings.registry_key]
           ):

            self._sorted_relative_strings_cache[self._settings.registry_key] = {
                self.info['name']: sorted([PARENTHESES_PATTERN.sub('', key) for key in
                                          self._relative_strings], key=len, reverse=True)
            }
        return self._sorted_relative_strings_cache[self._settings.registry_key][self.info['name']]

    def _get_split_relative_regex_cache(self):
        if (
            self._settings.registry_key not in self._split_relative_regex_cache or
            self.info['name'] not in self._split_relative_regex_cache[self._settings.registry_key]
           ):

            self._construct_split_relative_regex()
        return self._split_relative_regex_cache[self._settings.registry_key][self.info['name']]

    def _construct_split_relative_regex(self):
        known_relative_strings_group = "|".join(self._get_sorted_relative_strings_from_cache())
        if self._no_word_spacing:
            regex = "({})".format(known_relative_strings_group)
        else:
            regex = "(?<=(?:\\A|\\W|_))({})(?=(?:\\Z|\\W|_))".format(known_relative_strings_group)
        self._split_relative_regex_cache[self._settings.registry_key] = {
            self.info['name']: re.compile(regex, re.UNICODE | re.IGNORECASE)
        }

    def _get_match_relative_regex_cache(self):
        if (
            self._settings.registry_key not in self._match_relative_regex_cache or
            self.info['name'] not in self._match_relative_regex_cache[self._settings.registry_key]
           ):

            self._construct_match_relative_regex()
        return self._match_relative_regex_cache[self._settings.registry_key][self.info['name']]

    def _construct_match_relative_regex(self):
        known_relative_strings_group = "|".join(self._get_sorted_relative_strings_from_cache())
        regex = "^({})$".format(known_relative_strings_group)
        self._match_relative_regex_cache[self._settings.registry_key] = {
            self.info['name']: re.compile(regex, re.UNICODE | re.IGNORECASE)
        }


class NormalizedDictionary(Dictionary):

    def __init__(self, locale_info, settings=None):
        super(NormalizedDictionary, self).__init__(locale_info, settings)
        self._normalize()

    def _normalize(self):
        new_dict = {}
        conflicting_keys = []
        for key, value in self._dictionary.items():
            normalized = normalize_unicode(key)
            if key != normalized and normalized in self._dictionary:
                conflicting_keys.append(key)
            else:
                new_dict[normalized] = value
        for key in conflicting_keys:
            normalized = normalize_unicode(key)
            if key in (self.info.get('skip', []) + self.info.get('pertain', [])):
                new_dict[normalized] = self._dictionary[key]
        self._dictionary = new_dict
        self._relative_strings = list(map(normalize_unicode, self._relative_strings))
