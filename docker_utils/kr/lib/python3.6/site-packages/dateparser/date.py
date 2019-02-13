# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
import collections
from datetime import datetime, timedelta
from warnings import warn

import six
import regex as re
from dateutil.relativedelta import relativedelta

from dateparser.date_parser import date_parser
from dateparser.freshness_date_parser import freshness_date_parser
from dateparser.languages.loader import LocaleDataLoader
from dateparser.conf import apply_settings
from dateparser.utils import apply_timezone_from_settings


APOSTROPHE_LOOK_ALIKE_CHARS = [
    u'\N{RIGHT SINGLE QUOTATION MARK}',     # u'\u2019'
    u'\N{MODIFIER LETTER APOSTROPHE}',      # u'\u02bc'
    u'\N{MODIFIER LETTER TURNED COMMA}',    # u'\u02bb'
    u'\N{ARMENIAN APOSTROPHE}',             # u'\u055a'
    u'\N{LATIN SMALL LETTER SALTILLO}',     # u'\ua78c'
    u'\N{PRIME}',                           # u'\u2032'
    u'\N{REVERSED PRIME}',                  # u'\u2035'
    u'\N{MODIFIER LETTER PRIME}',           # u'\u02b9'
    u'\N{FULLWIDTH APOSTROPHE}',            # u'\uff07'
]

RE_NBSP = re.compile(u'\xa0', flags=re.UNICODE)
RE_SPACES = re.compile(r'\s+')
RE_TRIM_SPACES = re.compile(r'^\s+(\S.*?)\s+$')

RE_SANITIZE_SKIP = re.compile(r'\t|\n|\r|\u00bb|,\s\u0432|\u200e|\xb7|\u200f|\u064e|\u064f', flags=re.M)
RE_SANITIZE_RUSSIAN = re.compile(r'([\W\d])\u0433\.', flags=re.I | re.U)
RE_SANITIZE_PERIOD = re.compile(r'(?<=\D+)\.', flags=re.U)
RE_SANITIZE_ON = re.compile(r'^.*?on:\s+(.*)')
RE_SANITIZE_APOSTROPHE = re.compile(u'|'.join(APOSTROPHE_LOOK_ALIKE_CHARS))

RE_SEARCH_TIMESTAMP = re.compile(r'^\d{10}(?![^\d.])')


def sanitize_spaces(date_string):
    date_string = RE_NBSP.sub(' ', date_string)
    date_string = RE_SPACES.sub(' ', date_string)
    date_string = RE_TRIM_SPACES.sub(r'\1', date_string)
    return date_string


def date_range(begin, end, **kwargs):
    dateutil_error_prone_args = ['year', 'month', 'week', 'day', 'hour',
                                 'minute', 'second']
    for arg in dateutil_error_prone_args:
        if arg in kwargs:
            raise ValueError("Invalid argument: %s" % arg)

    step = relativedelta(**kwargs) if kwargs else relativedelta(days=1)

    date = begin
    while date < end:
        yield date
        date += step

    # handles edge-case when iterating months and last interval is < 30 days
    if kwargs.get('months', 0) > 0 and (date.year, date.month) == (end.year, end.month):
        yield end


def get_intersecting_periods(low, high, period='day'):
    if period not in ['year', 'month', 'week', 'day', 'hour', 'minute', 'second', 'microsecond']:
        raise ValueError("Invalid period: {}".format(period))

    if high <= low:
        return

    step = relativedelta(**{period + 's': 1})

    current_period_start = low
    if isinstance(current_period_start, datetime):
        reset_arguments = {}
        for test_period in ['microsecond', 'second', 'minute', 'hour']:
            if test_period == period:
                break
            else:
                reset_arguments[test_period] = 0
        current_period_start = current_period_start.replace(**reset_arguments)

    if period == 'week':
        current_period_start \
            = current_period_start - timedelta(days=current_period_start.weekday())
    elif period == 'month':
        current_period_start = current_period_start.replace(day=1)
    elif period == 'year':
        current_period_start = current_period_start.replace(month=1, day=1)

    while current_period_start < high:
        yield current_period_start
        current_period_start += step


def sanitize_date(date_string):
    date_string = RE_SANITIZE_SKIP.sub(' ', date_string)
    date_string = RE_SANITIZE_RUSSIAN.sub(r'\1 ', date_string)  # remove u'г.' (Russian for year) but not in words
    date_string = sanitize_spaces(date_string)
    date_string = RE_SANITIZE_PERIOD.sub('', date_string)
    date_string = RE_SANITIZE_ON.sub(r'\1', date_string)

    date_string = RE_SANITIZE_APOSTROPHE.sub(u"'", date_string)

    return date_string


def get_date_from_timestamp(date_string, settings):
    if RE_SEARCH_TIMESTAMP.search(date_string):
        date_obj = datetime.fromtimestamp(int(date_string[:10]))
        date_obj = apply_timezone_from_settings(date_obj, settings)
        return date_obj


def get_last_day_of_month(year, month):
    return calendar.monthrange(year, month)[1]


def parse_with_formats(date_string, date_formats, settings):
    """ Parse with formats and return a dictionary with 'period' and 'obj_date'.

    :returns: :class:`datetime.datetime`, dict or None

    """
    period = 'day'
    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_string, date_format)
        except ValueError:
            continue
        else:
            # If format does not include the day, use last day of the month
            # instead of first, because the first is usually out of range.
            if '%d' not in date_format:
                period = 'month'
                date_obj = date_obj.replace(
                    day=get_last_day_of_month(date_obj.year, date_obj.month))

            if not ('%y' in date_format or '%Y' in date_format):
                today = datetime.today()
                date_obj = date_obj.replace(year=today.year)

            date_obj = apply_timezone_from_settings(date_obj, settings)

            return {'date_obj': date_obj, 'period': period}
    else:
        return {'date_obj': None, 'period': period}


class _DateLocaleParser(object):
    DATE_FORMATS_ERROR_MESSAGE = "Date formats should be list, tuple or set of strings"

    def __init__(self, locale, date_string, date_formats, settings=None):
        self._settings = settings
        if isinstance(date_formats, six.string_types):
            warn(self.DATE_FORMATS_ERROR_MESSAGE, FutureWarning)
            date_formats = [date_formats]
        elif not (date_formats is None or isinstance(date_formats, (list, tuple, collections.Set))):
            raise TypeError(self.DATE_FORMATS_ERROR_MESSAGE)

        self.locale = locale
        self.date_string = date_string
        self.date_formats = date_formats
        self._translated_date = None
        self._translated_date_with_formatting = None

    @classmethod
    def parse(cls, locale, date_string, date_formats=None, settings=None):
        instance = cls(locale, date_string, date_formats, settings)
        return instance._parse()

    def _parse(self):
        for parser in (
            self._try_timestamp,
            self._try_freshness_parser,
            self._try_given_formats,
            self._try_parser,
            self._try_hardcoded_formats,
        ):
            date_obj = parser()
            if self._is_valid_date_obj(date_obj):
                return date_obj
        else:
            return None

    def _try_timestamp(self):
        return {
            'date_obj': get_date_from_timestamp(self.date_string, self._settings),
            'period': 'day',
        }

    def _try_freshness_parser(self):
        return freshness_date_parser.get_date_data(self._get_translated_date(), self._settings)

    def _try_parser(self):
        _order = self._settings.DATE_ORDER
        try:
            if self._settings.PREFER_LOCALE_DATE_ORDER:
                if self._settings._default:
                    self._settings.DATE_ORDER = self.locale.info.get('date_order', _order)
            date_obj, period = date_parser.parse(
                self._get_translated_date(), settings=self._settings)
            self._settings.DATE_ORDER = _order
            return {
                'date_obj': date_obj,
                'period': period,
            }
        except ValueError:
            self._settings.DATE_ORDER = _order
            return None

    def _try_given_formats(self):
        if not self.date_formats:
            return

        return parse_with_formats(
            self._get_translated_date_with_formatting(),
            self.date_formats, settings=self._settings
        )

    def _try_hardcoded_formats(self):
        hardcoded_date_formats = [
            '%B %d, %Y, %I:%M:%S %p',
            '%b %d, %Y at %I:%M %p',
            '%d %B %Y %H:%M:%S',
            '%A, %B %d, %Y',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]
        try:
            return parse_with_formats(
                self._get_translated_date_with_formatting(),
                hardcoded_date_formats,
                settings=self._settings
            )
        except TypeError:
            return None

    def _get_translated_date(self):
        if self._translated_date is None:
            self._translated_date = self.locale.translate(
                self.date_string, keep_formatting=False, settings=self._settings)
        return self._translated_date

    def _get_translated_date_with_formatting(self):
        if self._translated_date_with_formatting is None:
            self._translated_date_with_formatting = self.locale.translate(
                self.date_string, keep_formatting=True, settings=self._settings)
        return self._translated_date_with_formatting

    def _is_valid_date_obj(self, date_obj):
        if not isinstance(date_obj, dict):
            return False
        if len(date_obj) != 2:
            return False
        if 'date_obj' not in date_obj or 'period' not in date_obj:
            return False
        if not date_obj['date_obj']:
            return False
        if date_obj['period'] not in ('day', 'week', 'month', 'year'):
            return False

        return True


class DateDataParser(object):
    """
    Class which handles language detection, translation and subsequent generic parsing of
    string representing date and/or time.

    :param languages:
        A list of language codes, e.g. ['en', 'es', 'zh-Hant'].
        If locales are not given, languages and region are
        used to construct locales for translation.
    :type languages: list

    :param locales:
        A list of locale codes, e.g. ['fr-PF', 'qu-EC', 'af-NA'].
        The parser uses locales to translate date string.
    :type locales: list

    :param region:
        A region code, e.g. 'IN', '001', 'NE'.
        If locales are not given, languages and region are
        used to construct locales for translation.
    :type region: str|unicode

    :param try_previous_locales:
        If True, locales previously used to translate date are tried first.
    :type allow_redetect_language: bool

    :param use_given_order:
        If True, locales are tried for translation of date string
        in the order in which they are given.
    :type allow_redetect_language: bool

    :param settings:
        Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
    :type settings: dict

    :return: A parser instance

    :raises:
        ValueError - Unknown Language, TypeError - Languages argument must be a list
    """

    locale_loader = None

    @apply_settings
    def __init__(self, languages=None, locales=None, region=None, try_previous_locales=True,
                 use_given_order=False, settings=None):

        if not isinstance(languages, (list, tuple, collections.Set)) and languages is not None:
            raise TypeError("languages argument must be a list (%r given)" % type(languages))

        if not isinstance(locales, (list, tuple, collections.Set)) and locales is not None:
            raise TypeError("locales argument must be a list (%r given)" % type(locales))

        if not isinstance(region, six.string_types) and region is not None:
            raise TypeError("region argument must be str or unicode (%r given)" % type(region))

        if not isinstance(try_previous_locales, bool):
            raise TypeError("try_previous_locales argument must be a boolean (%r given)"
                            % type(try_previous_locales))

        if not isinstance(use_given_order, bool):
            raise TypeError("use_given_order argument must be a boolean (%r given)"
                            % type(use_given_order))

        if not locales and use_given_order:
            raise ValueError("locales must be given if use_given_order is True")

        self._settings = settings
        self.try_previous_locales = try_previous_locales
        self.use_given_order = use_given_order
        self.languages = languages
        self.locales = locales
        self.region = region
        self.previous_locales = []

    def get_date_data(self, date_string, date_formats=None):
        """
        Parse string representing date and/or time in recognizable localized formats.
        Supports parsing multiple languages and timezones.

        :param date_string:
            A string representing date and/or time in a recognizably valid format.
        :type date_string: str|unicode
        :param date_formats:
            A list of format strings using directives as given
            `here <https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior>`_.
            The parser applies formats one by one, taking into account the detected languages.
        :type date_formats: list

        :return: a dict mapping keys to :mod:`datetime.datetime` object and *period*. For example:
            {'date_obj': datetime.datetime(2015, 6, 1, 0, 0), 'period': u'day'}

        :raises: ValueError - Unknown Language

        .. note:: *Period* values can be a 'day' (default), 'week', 'month', 'year'.

        *Period* represents the granularity of date parsed from the given string.

        In the example below, since no day information is present, the day is assumed to be current
        day ``16`` from *current date* (which is June 16, 2015, at the moment of writing this).
        Hence, the level of precision is ``month``:

            >>> DateDataParser().get_date_data(u'March 2015')
            {'date_obj': datetime.datetime(2015, 3, 16, 0, 0), 'period': u'month'}

        Similarly, for date strings with no day and month information present, level of precision
        is ``year`` and day ``16`` and month ``6`` are from *current_date*.

            >>> DateDataParser().get_date_data(u'2014')
            {'date_obj': datetime.datetime(2014, 6, 16, 0, 0), 'period': u'year'}

        Dates with time zone indications or UTC offsets are returned in UTC time unless
        specified using `Settings`_.

            >>> DateDataParser().get_date_data(u'23 March 2000, 1:21 PM CET')
            {'date_obj': datetime.datetime(2000, 3, 23, 14, 21), 'period': 'day'}

        """
        if not(isinstance(date_string, six.text_type) or isinstance(date_string, six.string_types)):
            raise TypeError('Input type must be str or unicode')

        if isinstance(date_string, bytes):
            date_string = date_string.decode('utf-8')

        res = parse_with_formats(date_string, date_formats or [], self._settings)
        if res['date_obj']:
            return res

        date_string = sanitize_date(date_string)

        for locale in self._get_applicable_locales(date_string):
            parsed_date = _DateLocaleParser.parse(
                locale, date_string, date_formats, settings=self._settings)
            if parsed_date:
                parsed_date['locale'] = locale.shortname
                if self.try_previous_locales:
                    self.previous_locales.insert(0, locale)
                return parsed_date
        else:
            return {'date_obj': None, 'period': 'day', 'locale': None}

    def get_date_tuple(self, *args, **kwargs):
        date_tuple = collections.namedtuple('DateData', 'date_obj period locale')
        date_data = self.get_date_data(*args, **kwargs)
        return date_tuple(**date_data)

    def _get_applicable_locales(self, date_string):
        if self.try_previous_locales:
            for locale in self.previous_locales:
                if self._is_applicable_locale(locale, date_string):
                    yield locale

        for locale in self._get_locale_loader().get_locales(
                languages=self.languages, locales=self.locales, region=self.region,
                use_given_order=self.use_given_order):
            if self._is_applicable_locale(locale, date_string):
                yield locale

    def _is_applicable_locale(self, locale, date_string):
        return (
            locale.is_applicable(date_string, strip_timezone=False, settings=self._settings) or
            locale.is_applicable(date_string, strip_timezone=True, settings=self._settings)
            )

    @classmethod
    def _get_locale_loader(cls):
        if not cls.locale_loader:
            cls.locale_loader = LocaleDataLoader()
        return cls.locale_loader
