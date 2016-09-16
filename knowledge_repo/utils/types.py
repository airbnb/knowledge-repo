import sys

__all__ = ['str_types']

if sys.version_info.major > 2:
    str_types = (str,)
else:
    str_types = (str, unicode)
