import datetime

import six
from past.builtins import basestring

from ..post import HEADER_OPTIONAL_FIELD_TYPES, HEADER_REQUIRED_FIELD_TYPES
from ..postprocessor import KnowledgePostProcessor


class FormatChecks(KnowledgePostProcessor):
    _registry_keys = ['format_checks']

    def process(self, kp):
        headers = kp.headers
        for field, typ, input in HEADER_REQUIRED_FIELD_TYPES:
            assert field in headers, "Required field `{}` missing from headers.".format(
                field)
            assert isinstance(headers[field], typ), "Value for field `{}` is of type {}, and needs to be of type {}.".format(
                field, type(headers[field]), typ)
        for field, typ, input in HEADER_OPTIONAL_FIELD_TYPES:
            if field in headers:
                assert isinstance(headers[field], typ), "Value for field `{}` is of type {}, and needs to be of type {}.".format(
                    field, type(headers[field]), typ)
