import datetime
from past.builtins import basestring

from ..postprocessor import KnowledgePostProcessor

REQUIRED_FIELD_TYPES = {
    'title': str,
    'authors': list,
    'created_at': datetime.datetime,
    'tldr': basestring,
    'tags': list
}

OPTIONAL_FIELD_TYPES = {
    'path': str,
    'updated_at': datetime.datetime,
    'private': bool,   # If true, this post starts out private
    'allowed_groups': list,
    'thumbnail': (int, str)
}


class FormatChecks(KnowledgePostProcessor):
    _registry_keys = ['format_checks']

    @classmethod
    def process(cls, kp):
        headers = kp.headers
        for field, typ in REQUIRED_FIELD_TYPES.items():
            assert field in headers, "Required field `{}` missing from headers.".format(
                field)
            assert isinstance(headers[field], typ), "Value for field `{}` is of type {}, and needs to be of type {}.".format(
                field, type(headers[field]), typ)
        for field, typ in OPTIONAL_FIELD_TYPES.items():
            if field in headers:
                assert isinstance(headers[field], typ), "Value for field `{}` is of type {}, and needs to be of type {}.".format(
                    field, type(headers[field]), typ)
