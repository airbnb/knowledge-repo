import sys

from sqlalchemy import Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT

__all__ = ['str_types']

if sys.version_info.major > 2:
    str_types = (str,)
else:
    str_types = (str, unicode)


def MediumText():
    return Text().with_variant(MEDIUMTEXT(), 'mysql')
