from ..constants import FORMAT_CHECKS
from ..post import HEADER_OPTIONAL_FIELD_TYPES, HEADER_REQUIRED_FIELD_TYPES
from ..postprocessor import KnowledgePostProcessor


class FormatChecks(KnowledgePostProcessor):
    _registry_keys = [FORMAT_CHECKS]

    def process(self, kp):
        headers = kp.headers
        for field, typ, _ in HEADER_REQUIRED_FIELD_TYPES:
            assert field in headers, \
                f"Required field `{field}` missing from headers."
        for field, typ, _ in \
                HEADER_REQUIRED_FIELD_TYPES + HEADER_OPTIONAL_FIELD_TYPES:
            if field in headers:
                header_field = headers[field]
                assert isinstance(header_field, typ), \
                    (f"Value for field `{field}` is of type "
                     f"{type(header_field)}, and needs to be of type {typ}.")
