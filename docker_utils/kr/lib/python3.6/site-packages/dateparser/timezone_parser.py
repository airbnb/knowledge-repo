# -*- coding: utf-8 -*-
import regex as re
from datetime import datetime, timedelta, tzinfo

from .timezones import timezone_info_list


class StaticTzInfo(tzinfo):

    def __init__(self, name, offset):
        self.__offset = offset
        self.__name = name

    def tzname(self, dt):
        return self.__name

    def utcoffset(self, dt):
        return self.__offset

    def dst(self, dt):
        return timedelta(0)

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.__name)

    def localize(self, dt, is_dst=False):
        if dt.tzinfo is not None:
            raise ValueError('Not naive datetime (tzinfo is already set)')
        return dt.replace(tzinfo=self)


def pop_tz_offset_from_string(date_string, as_offset=True):
    for name, info in _tz_offsets:
        timezone_re = info['regex']
        timezone_match = timezone_re.search(date_string)
        if timezone_match:
            start, stop = timezone_match.span()
            date_string = date_string[:start + 1] + date_string[stop:]
            return date_string, StaticTzInfo(name, info['offset']) if as_offset else name
    else:
        return date_string, None


def convert_to_local_tz(datetime_obj, datetime_tz_offset):
    return datetime_obj - datetime_tz_offset + local_tz_offset


def get_tz_offsets():

    def get_offset(tz_obj, regex, repl='', replw=''):
        return (
            tz_obj[0],
            {
                'regex': re.compile(re.sub(repl, replw, regex % tz_obj[0]), re.IGNORECASE),
                'offset': timedelta(seconds=tz_obj[1])
            }
        )

    for tz_info in timezone_info_list:
        for regex in tz_info['regex_patterns']:
            for tz_obj in tz_info['timezones']:
                yield get_offset(tz_obj, regex)

            # alternate patterns
            for replace, replacewith in tz_info.get('replace', []):
                for tz_obj in tz_info['timezones']:
                    yield get_offset(tz_obj, regex, repl=replace, replw=replacewith)


def get_local_tz_offset():
    offset = datetime.now() - datetime.utcnow()
    offset = timedelta(days=offset.days, seconds=round(offset.seconds, -1))
    return offset


_tz_offsets = list(get_tz_offsets())
local_tz_offset = get_local_tz_offset()
