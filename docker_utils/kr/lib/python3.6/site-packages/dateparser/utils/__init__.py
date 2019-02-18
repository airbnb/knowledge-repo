# -*- coding: utf-8 -*-
import logging
import types
import unicodedata

import regex as re
from tzlocal import get_localzone
from pytz import UTC, timezone, UnknownTimeZoneError
from collections import OrderedDict

from dateparser.timezone_parser import _tz_offsets, StaticTzInfo


def strip_braces(date_string):
    return re.sub(r'[{}()<>\[\]]+', '', date_string)


def normalize_unicode(string, form='NFKD'):
    if isinstance(string, bytes):
        string = string.decode('utf-8')

    return ''.join(
        (c for c in unicodedata.normalize(form, string)
         if unicodedata.category(c) != 'Mn'))


def combine_dicts(primary_dict, supplementary_dict):
    combined_dict = OrderedDict()
    for key, value in primary_dict.items():
        if key in supplementary_dict:
            if isinstance(value, list):
                combined_dict[key] = value + supplementary_dict[key]
            elif isinstance(value, dict):
                combined_dict[key] = combine_dicts(value, supplementary_dict[key])
            else:
                combined_dict[key] = supplementary_dict[key]
        else:
            combined_dict[key] = primary_dict[key]
    remaining_keys = [key for key in supplementary_dict.keys() if key not in primary_dict.keys()]
    for key in remaining_keys:
        combined_dict[key] = supplementary_dict[key]
    return combined_dict


def convert_to_unicode(info):
    unicode_info = OrderedDict()
    for key, value in info.items():
        if isinstance(key, bytes):
            key = key.decode('utf-8')
        if isinstance(value, list):
            for i, v in enumerate(value):
                if isinstance(v, dict):
                    value[i] = convert_to_unicode(v)
                elif isinstance(v, bytes):
                    value[i] = v.decode('utf-8')
        elif isinstance(value, dict):
            value = convert_to_unicode(value)
        elif isinstance(value, bytes):
            value = value.decode('utf-8')
        unicode_info[key] = value
    return unicode_info


def find_date_separator(format):
    m = re.search(r'(?:(?:%[dbBmaA])(\W))+', format)
    if m:
        return m.group(1)


def localize_timezone(date_time, tz_string):
    if date_time.tzinfo:
        return date_time

    tz = None

    try:
        tz = timezone(tz_string)
    except UnknownTimeZoneError as e:
        for name, info in _tz_offsets:
            if info['regex'].search(' %s' % tz_string):
                tz = StaticTzInfo(name, info['offset'])
                break
        else:
            raise e

    return tz.localize(date_time)


def apply_tzdatabase_timezone(date_time, pytz_string):
    usr_timezone = timezone(pytz_string)

    if date_time.tzinfo != usr_timezone:
        date_time = date_time.astimezone(usr_timezone)

    return date_time


def apply_dateparser_timezone(utc_datetime, offset_or_timezone_abb):
    for name, info in _tz_offsets:
        if info['regex'].search(' %s' % offset_or_timezone_abb):
            tz = StaticTzInfo(name, info['offset'])
            return utc_datetime.astimezone(tz)


def apply_timezone(date_time, tz_string):
    if not date_time.tzinfo:
        date_time = UTC.localize(date_time)

    new_datetime = apply_dateparser_timezone(date_time, tz_string)

    if not new_datetime:
        new_datetime = apply_tzdatabase_timezone(date_time, tz_string)

    return new_datetime


def apply_timezone_from_settings(date_obj, settings):
    tz = get_localzone()
    if settings is None:
        return date_obj

    if 'local' in settings.TIMEZONE.lower():
        date_obj = tz.localize(date_obj)
    else:
        date_obj = localize_timezone(date_obj, settings.TIMEZONE)

    if settings.TO_TIMEZONE:
        date_obj = apply_timezone(date_obj, settings.TO_TIMEZONE)

    if settings.RETURN_AS_TIMEZONE_AWARE is not True:
        date_obj = date_obj.replace(tzinfo=None)

    return date_obj


def registry(cls):
    def choose(creator):
        def constructor(cls, *args, **kwargs):
            key = cls.get_key(*args, **kwargs)

            if not hasattr(cls, "__registry_dict"):
                setattr(cls, "__registry_dict", {})
            registry_dict = getattr(cls, "__registry_dict")

            if key not in registry_dict:
                registry_dict[key] = creator(cls, *args)
                setattr(registry_dict[key], 'registry_key', key)
            return registry_dict[key]
        return staticmethod(constructor)

    if not (hasattr(cls, "get_key")
            and isinstance(cls.get_key, types.MethodType)
            and cls.get_key.__self__ is cls):
        raise NotImplementedError("Registry classes require to implement class method get_key")

    setattr(cls, '__new__', choose(cls.__new__))
    return cls


def get_logger():
    setup_logging()
    return logging.getLogger('dateparser')


def setup_logging():
    if len(logging.root.handlers):
        return

    config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'console': {
                'format': "%(asctime)s %(levelname)s: [%(name)s] %(message)s",
            },
        },
        'handlers': {
            'console': {
                'level': logging.DEBUG,
                'class': "logging.StreamHandler",
                'formatter': "console",
                'stream': "ext://sys.stdout",
            },
        },
        'root': {
            'level': logging.DEBUG,
            'handlers': ["console"],
        },
    }
    logging.config.dictConfig(config)
