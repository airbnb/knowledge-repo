# coding: utf-8

from umalqurra.hijri_date import HijriDate as hj
from umalqurra.ummalqura_arrray import UmalqurraArray
from dateparser.calendars import non_gregorian_parser


class hijri(object):

    @classmethod
    def to_gregorian(cls, year=None, month=None, day=None):
        h = hj(year=year, month=month, day=day)
        return int(h.year_gr), int(h.month_gr), int(h.day_gr)

    @classmethod
    def from_gregorian(cls, year=None, month=None, day=None):
        h = hj(year=year, month=month, day=day, gr=True)
        return int(h.year), int(h.month), int(h.day)

    @classmethod
    def month_length(cls, year, month):
        iy = year
        im = month
        id = 1
        ii = iy - 1
        iln = (ii * 12) + 1 + (im - 1)
        i = iln - 16260
        mcjdn = id + UmalqurraArray.ummalqura_dat[i - 1] - 1
        index = UmalqurraArray.get_index(mcjdn)
        ml = UmalqurraArray.ummalqura_dat[index] - UmalqurraArray.ummalqura_dat[index - 1]
        return ml


class HijriDate(object):
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def weekday(self):
        for week in hijri.monthcalendar(self.year, self.month):
            for idx, day in enumerate(week):
                if day == self.day:
                    return idx


class hijri_parser(non_gregorian_parser):

    calendar_converter = hijri
    default_year = 1389
    default_month = 1
    default_day = 1
    non_gregorian_date_cls = HijriDate

    _time_conventions = {
        'am': [u"صباحاً"],
        'pm': [u"مساءً"],
    }

    # TODO: Implement arabic to latin translation
    # replace_ methods according to the way native speakers write

    @classmethod
    def _replace_time_conventions(cls, source):
        result = source
        for latin, arabics in cls._time_conventions.items():
            for arabic in arabics:
                result = result.replace(arabic, latin)
        return result
