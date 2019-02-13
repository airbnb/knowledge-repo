# coding: utf-8
import calendar
import regex as re

from io import StringIO
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta

from dateparser.utils.strptime import strptime


NSP_COMPATIBLE = re.compile(r'\D+')
MERIDIAN = re.compile(r'am|pm')
MICROSECOND = re.compile(r'\d{1,6}')


def no_space_parser_eligibile(datestring):
    src = NSP_COMPATIBLE.search(datestring)
    if not src or ':' == src.group():
        return True

    return False


def get_unresolved_attrs(parser_object):
    attrs = ['year', 'month', 'day']
    seen = []
    unseen = []
    for attr in attrs:
        if getattr(parser_object, attr, None) is not None:
            seen.append(attr)
        else:
            unseen.append(attr)
    return seen, unseen


def resolve_date_order(order, lst=None):
    chart = {
        'MDY': '%m%d%y',
        'MYD': '%m%y%d',
        'YMD': '%y%m%d',
        'YDM': '%y%d%m',
        'DMY': '%d%m%y',
        'DYM': '%d%y%m',
    }

    chart_list = {
        'MDY': ['month', 'day', 'year'],
        'MYD': ['month', 'year', 'day'],
        'YMD': ['year', 'month', 'day'],
        'YDM': ['year', 'day', 'month'],
        'DMY': ['day', 'month', 'year'],
        'DYM': ['day', 'year', 'month'],
    }

    return chart_list[order] if lst else chart[order]


def parse(datestring, settings):
    exceptions = []
    for parser in [_parser.parse, _no_spaces_parser.parse]:
        try:
            res = parser(datestring, settings)
            if res:
                return res
        except Exception as e:
            exceptions.append(e)
    else:
        raise exceptions.pop(-1)


class _time_parser(object):
    time_directives = [
        '%H:%M:%S',
        '%I:%M:%S %p',
        '%H:%M',
        '%I:%M %p',
        '%I %p',
        '%H:%M:%S.%f',
        '%I:%M:%S.%f %p',
    ]

    def __call__(self, timestring):
        _timestring = timestring
        for directive in self.time_directives:
            try:
                return strptime(timestring.strip(), directive).time()
            except ValueError:
                pass
        else:
            raise ValueError('%s does not seem to be a valid time string' % _timestring)

time_parser = _time_parser()


class _no_spaces_parser(object):
    _dateformats = [
        '%Y%m%d', '%Y%d%m', '%m%Y%d',
        '%m%d%Y', '%d%Y%m', '%d%m%Y',
        '%y%m%d', '%y%d%m', '%m%y%d',
        '%m%d%y', '%d%y%m', '%d%m%y'
    ]

    _preferred_formats = ['%Y%m%d%H%M', '%Y%m%d%H%M%S', '%Y%m%d%H%M%S.%f']

    _timeformats = ['%H%M%S.%f', '%H%M%S', '%H%M', '%H']

    period = {
        'day': ['%d', '%H', '%M', '%S'],
        'month': ['%m']
    }

    _default_order = resolve_date_order('MDY')

    def __init__(self, *args, **kwargs):

        self._all = (self._dateformats +
                     [x+y for x in self._dateformats for y in self._timeformats] +
                     self._timeformats)

        self.date_formats = {
            '%m%d%y': (
                self._preferred_formats +
                sorted(self._all, key=lambda x: x.lower().startswith('%m%d%y'), reverse=True)
            ),
            '%m%y%d': sorted(self._all, key=lambda x: x.lower().startswith('%m%y%d'), reverse=True),
            '%y%m%d': sorted(self._all, key=lambda x: x.lower().startswith('%y%m%d'), reverse=True),
            '%y%d%m': sorted(self._all, key=lambda x: x.lower().startswith('%y%d%m'), reverse=True),
            '%d%m%y': sorted(self._all, key=lambda x: x.lower().startswith('%d%m%y'), reverse=True),
            '%d%y%m': sorted(self._all, key=lambda x: x.lower().startswith('%d%y%m'), reverse=True),
        }

    @classmethod
    def _get_period(cls, format_string):
        for pname, pdrv in sorted(cls.period.items(), key=lambda x: x[0]):
            for drv in pdrv:
                if drv in format_string:
                    return pname
        else:
            return 'year'

    @classmethod
    def parse(cls, datestring, settings):
        if not no_space_parser_eligibile(datestring):
            return

        datestring = datestring.replace(':', '')
        tokens = tokenizer(datestring)
        if settings.DATE_ORDER:
            order = resolve_date_order(settings.DATE_ORDER)
        else:
            order = cls._default_order
        nsp = cls()
        ambiguous_date = None
        for token, _ in tokens.tokenize():
            for fmt in nsp.date_formats[order]:
                try:
                    dt = strptime(token, fmt), cls._get_period(fmt)
                    if len(str(dt[0].year)) < 4:
                        ambiguous_date = dt
                        continue
                    return dt
                except:
                    pass
        else:
            if ambiguous_date:
                return ambiguous_date
            else:
                raise ValueError('Unable to parse date from: %s' % datestring)


class _parser(object):

    alpha_directives = OrderedDict([
        ('weekday', ['%A', '%a']),
        ('month', ['%B', '%b']),
    ])

    num_directives = {
        'month': ['%m'],
        'day': ['%d'],
        'year': ['%y', '%Y'],
    }


    def __init__(self, tokens, settings):
        self.settings = settings
        self.tokens = list(tokens)
        self.filtered_tokens = [t for t in self.tokens if t[1] <= 1]

        self.unset_tokens = []

        self.day = None
        self.month = None
        self.year = None
        self.time = None

        self.auto_order = []

        self._token_day = None
        self._token_month = None
        self._token_year = None
        self._token_time = None

        self.ordered_num_directives = OrderedDict(
            (k, self.num_directives[k])
            for k in (resolve_date_order(settings.DATE_ORDER, lst=True))
        )

        skip_index = []
        skip_component = None
        for index, token_type in enumerate(self.filtered_tokens):

            if index in skip_index:
                continue

            token, type = token_type

            if token in settings.SKIP_TOKENS_PARSER:
                continue

            if self.time is None:
                try:
                    microsecond = MICROSECOND.search(self.filtered_tokens[index+1][0]).group()
                    _is_after_time_token = token.index(":")
                    _is_after_period = self.tokens[
                        self.tokens.index((token, 0)) + 1][0].index('.')
                except:
                    microsecond = None

                if microsecond:
                    mindex = index + 2
                else:
                    mindex = index + 1

                try:
                    meridian = MERIDIAN.search(self.filtered_tokens[mindex][0]).group()
                except:
                    meridian = None

                if any([':' in token, meridian, microsecond]):
                    if meridian and not microsecond:
                        self._token_time = '%s %s' % (token, meridian)
                        skip_index.append(mindex)
                    elif microsecond and not meridian:
                        self._token_time = '%s.%s' % (token, microsecond)
                        skip_index.append(index + 1)
                    elif meridian and microsecond:
                        self._token_time = '%s.%s %s' % (token, microsecond, meridian)
                        skip_index.append(index + 1)
                        skip_index.append(mindex)
                    else:
                        self._token_time = token
                    self.time = lambda: time_parser(self._token_time)
                    continue

            results = self._parse(type, token, settings.FUZZY, skip_component=skip_component)
            for res in results:
                if len(token) == 4 and res[0] == 'year':
                    skip_component = 'year'
                setattr(self, *res)

        known, unknown = get_unresolved_attrs(self)
        params = {}
        for attr in known:
            params.update({attr: getattr(self, attr)})
        for attr in unknown:
            for token, type, _ in self.unset_tokens:
                if type == 0:
                    params.update({attr: int(token)})
                    datetime(**params)
                    setattr(self, '_token_%s' % attr, token)
                    setattr(self, attr, int(token))

    def _get_period(self):
        for period in ['time', 'day']:
            if getattr(self, period, None):
                return 'day'

        for period in ['month', 'year']:
            if getattr(self, period, None):
                return period

        if self._results():
            return 'day'

    def _get_datetime_obj(self, **params):
        try:
            return datetime(**params)
        except ValueError as e:
            error_text = getattr(e, 'message', None) or e.__str__()
            error_msgs = ['day is out of range', 'day must be in']
            if (
                (error_msgs[0] in error_text or error_msgs[1] in error_text) and
                not(self._token_day or hasattr(self, '_token_weekday'))
            ):
                _, tail = calendar.monthrange(params['year'], params['month'])
                params['day'] = tail
                return datetime(**params)
            else:
                raise e

    def _set_relative_base(self):
        self.now = self.settings.RELATIVE_BASE
        if not self.now:
            self.now = datetime.utcnow()

    def _get_datetime_obj_params(self):
        if not self.now:
            self._set_relative_base()

        params = {
            'day': self.day or self.now.day,
            'month': self.month or self.now.month,
            'year': self.year or self.now.year,
            'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0,
        }
        return params

    def _get_date_obj(self, token, directive):
        return strptime(token, directive)

    def _results(self):
        if self.settings.STRICT_PARSING:
            errors = []
            if not self.day:
                errors.append('Day')
            if not self.month:
                errors.append('Month')
            if not self.year:
                errors.append('Year')
            if errors:
                raise ValueError('%s not found in the date string' % ''.join(errors))

        self._set_relative_base()

        time = self.time() if self.time is not None else None

        if self.settings.FUZZY:
            attr_truth_values = []
            for attr in ['day', 'month', 'year', 'time']:
                attr_truth_values.append(getattr(self, attr, False))

            if not any(attr_truth_values):
                raise ValueError('Nothing date like found')

        params = self._get_datetime_obj_params()

        if time:
            params.update(dict(hour=time.hour,
                               minute=time.minute,
                               second=time.second,
                               microsecond=time.microsecond))

        return self._get_datetime_obj(**params)

    def _correct_for_time_frame(self, dateobj):
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

        token_weekday, _ = getattr(self, '_token_weekday', (None, None))

        if token_weekday and not(self._token_year or self._token_month or self._token_day):
            day_index = calendar.weekday(dateobj.year, dateobj.month, dateobj.day)
            day = token_weekday[:3].lower()
            steps = 0
            if 'future' in self.settings.PREFER_DATES_FROM:
                if days[day_index] == day:
                    steps = 7
                else:
                    while days[day_index] != day:
                        day_index = (day_index + 1) % 7
                        steps += 1
                delta = timedelta(days=steps)
            else:
                if days[day_index] == day:
                    steps = 7
                else:
                    while days[day_index] != day:
                        day_index -= 1
                        steps += 1
                delta = timedelta(days=-steps)

            dateobj = dateobj + delta

        if self.month and not self.year:
            if self.now < dateobj:
                if 'past' in self.settings.PREFER_DATES_FROM:
                    dateobj = dateobj.replace(year=dateobj.year - 1)
            else:
                if 'future' in self.settings.PREFER_DATES_FROM:
                    dateobj = dateobj.replace(year=dateobj.year + 1)

        if self._token_year and len(self._token_year[0]) == 2:
            if self.now < dateobj:
                if 'past' in self.settings.PREFER_DATES_FROM:
                    dateobj = dateobj.replace(year=dateobj.year - 100)
            else:
                if 'future' in self.settings.PREFER_DATES_FROM:
                    dateobj = dateobj.replace(year=dateobj.year + 100)

        if self._token_time and not any([self._token_year,
                                         self._token_month,
                                         self._token_day,
                                         hasattr(self, '_token_weekday')]):
            if 'past' in self.settings.PREFER_DATES_FROM:
                if self.now.time() < dateobj.time():
                    dateobj = dateobj + timedelta(days=-1)
            if 'future' in self.settings.PREFER_DATES_FROM:
                if self.now.time() > dateobj.time():
                    dateobj = dateobj + timedelta(days=1)

        return dateobj

    def _correct_for_day(self, dateobj):
        if (
            getattr(self, '_token_day', None) or
            getattr(self, '_token_weekday', None) or
            getattr(self, '_token_time', None)
        ):
            return dateobj

        _, tail = calendar.monthrange(dateobj.year, dateobj.month)
        options = {
            'first': 1,
            'last': tail,
            'current': self.now.day
        }

        try:
            return dateobj.replace(day=options[self.settings.PREFER_DAY_OF_MONTH])
        except ValueError:
            return dateobj.replace(day=options['last'])

    @classmethod
    def parse(cls, datestring, settings):
        tokens = tokenizer(datestring)
        po = cls(tokens.tokenize(), settings)
        dateobj = po._results()

        # correction for past, future if applicable
        dateobj = po._correct_for_time_frame(dateobj)

        # correction for preference of day: beginning, current, end
        dateobj = po._correct_for_day(dateobj)

        return dateobj, po._get_period()

    def _parse(self, type, token, fuzzy, skip_component=None):

        def set_and_return(token, type, component, dateobj, skip_date_order=False):
            if not skip_date_order:
                self.auto_order.append(component)
            setattr(self, '_token_%s' % component, (token, type))
            return [(component, getattr(dateobj, component))]

        def parse_number(token, skip_component=None):
            type = 0

            for component, directives in self.ordered_num_directives.items():
                if skip_component == component:
                    continue
                for directive in directives:
                    try:
                        do = self._get_date_obj(token, directive)
                        prev_value = getattr(self, component, None)
                        if not prev_value:
                            return set_and_return(token, type, component, do)
                        else:
                            try:
                                prev_token, prev_type = getattr(self, '_token_%s' % component)
                                if prev_type == type:
                                    do = self._get_date_obj(prev_token, directive)
                            except ValueError:
                                self.unset_tokens.append((prev_token, prev_type, component))
                                return set_and_return(token, type, component, do)
                    except ValueError:
                        pass
            else:
                if not fuzzy:
                    raise ValueError('Unable to parse: %s' % token)
                else:
                    return []

        def parse_alpha(token, skip_component=None):
            type = 1

            for component, directives in self.alpha_directives.items():
                if skip_component == component:
                    continue
                for directive in directives:
                    try:
                        do = self._get_date_obj(token, directive)
                        prev_value = getattr(self, component, None)
                        if not prev_value:
                            return set_and_return(token, type, component, do, skip_date_order=True)
                        elif component == 'month':
                            index = self.auto_order.index('month')
                            self.auto_order[index] = 'day'
                            setattr(self, '_token_day', self._token_month)
                            setattr(self, '_token_month', (token, type))
                            return [(component, getattr(do, component)), ('day', prev_value)]
                    except:
                        pass
            else:
                if not fuzzy:
                    raise ValueError('Unable to parse: %s' % token)
                else:
                    return []

        handlers = {0: parse_number, 1: parse_alpha}
        return handlers[type](token, skip_component)


class tokenizer(object):
    digits = u'0123456789:'
    letters = u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    nonwords = u"./\()\"',.;<>~!@#$%^&*|+=[]{}`~?-     "

    def _isletter(self, tkn): return tkn in self.letters

    def _isdigit(self, tkn): return tkn in self.digits

    def _isnonword(self, tkn): return tkn in self.nonwords

    def __init__(self, ds):
        self.instream = StringIO(ds)

    def _switch(self, chara, charb):
        if self._isdigit(chara):
            return 0, not self._isdigit(charb)

        if self._isletter(chara):
            return 1, not self._isletter(charb)

        if self._isnonword(chara):
            return 2, not self._isnonword(charb)

        return '', True

    def tokenize(self):
        token = ''
        EOF = False

        while not EOF:
            nextchar = self.instream.read(1)

            if not nextchar:
                EOF = True
                type, _ = self._switch(token[-1], nextchar)
                yield token, type
                return

            if token:
                type, switch = self._switch(token[-1], nextchar)

                if not switch:
                    token += nextchar
                else:
                    yield token, type
                    token = nextchar
            else:
                token += nextchar
