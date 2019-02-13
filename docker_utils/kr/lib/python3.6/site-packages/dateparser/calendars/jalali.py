# coding: utf-8

from __future__ import unicode_literals

from . import CalendarBase
from dateparser.calendars.jalali_parser import jalali_parser


class JalaliCalendar(CalendarBase):
    """Calendar class for Jalali calendar."""

    parser = jalali_parser
