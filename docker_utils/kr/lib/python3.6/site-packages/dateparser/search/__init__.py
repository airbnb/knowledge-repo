# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dateparser.search.search import DateSearchWithDetection

_search_with_detection = DateSearchWithDetection()


def search_dates(text, languages=None, settings=None):
    """Find all substrings of the given string which represent date and/or time and parse them.

        :param text:
            A string in a natural language which may contain date and/or time expressions.
        :type text: str|unicode
        :param languages:
            A list of two letters language codes.e.g. ['en', 'es']. If languages are given, it will not attempt
            to detect the language.
        :type languages: list
        :param settings:
               Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
        :type settings: dict


        :return: Returns list of tuples containing pairs:
                 substrings representing date and/or time and corresponding :mod:`datetime.datetime` object.
                 Returns None if no dates that can be parsed are found.
        :rtype: list
        :raises: ValueError - Unknown Language

        >>> search_dates('The first artificial Earth satellite was launched on 4 October 1957.')
        [('on 4 October 1957', datetime.datetime(1957, 10, 4, 0, 0))]

        """
    result = _search_with_detection.search_dates(text=text, languages=languages, settings=settings)
    if result['Dates']:
        return result['Dates']
