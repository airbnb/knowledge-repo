# -*- coding: utf-8 -*-
__version__ = '0.7.0'

from .date import DateDataParser
from .conf import apply_settings

_default_parser = DateDataParser()


@apply_settings
def parse(date_string, date_formats=None, languages=None, locales=None, region=None, settings=None):
    """Parse date and time from given date string.

    :param date_string:
        A string representing date and/or time in a recognizably valid format.
    :type date_string: str|unicode

    :param date_formats:
        A list of format strings using directives as given
        `here <https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior>`_.
        The parser applies formats one by one, taking into account the detected languages/locales.
    :type date_formats: list

    :param languages:
        A list of language codes, e.g. ['en', 'es', 'zh-Hant'].
        If locales are not given, languages and region are used to construct locales for translation.
    :type languages: list

    :param locales:
        A list of locale codes, e.g. ['fr-PF', 'qu-EC', 'af-NA'].
        The parser uses locales to translate date string.
    :type locales: list

    :param region:
        A region code, e.g. 'IN', '001', 'NE'.
        If locales are not given, languages and region are used to construct locales for translation.
    :type region: str|unicode

    :param settings:
        Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
    :type settings: dict

    :return: Returns :class:`datetime <datetime.datetime>` representing parsed date if successful, else returns None
    :rtype: :class:`datetime <datetime.datetime>`.
    :raises: ValueError - Unknown Language
    """
    parser = _default_parser

    if any([languages, locales, region, not settings._default]):
        parser = DateDataParser(languages=languages, locales=locales,
                                region=region, settings=settings)

    data = parser.get_date_data(date_string, date_formats)

    if data:
        return data['date_obj']
