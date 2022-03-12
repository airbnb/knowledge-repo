from sqlalchemy import Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT


def MediumText():
    return Text().with_variant(MEDIUMTEXT(), 'mysql')
