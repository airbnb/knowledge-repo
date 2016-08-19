import datetime

from ..postprocessor import KnowledgePostProcessor

REQUIRED_FIELD_TYPES = {
    'title': str,
    'authors': list,
    'created_at': datetime.datetime,
    'tldr': str,
    'tags': list
}

OPTIONAL_FIELD_TYPES = {
    'path': str,
    'updated_at': datetime.datetime
}


class FormatChecks(KnowledgePostProcessor):
    '''
    Use this to bootstrap your own KnowledgePostProcessor.
    '''
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
