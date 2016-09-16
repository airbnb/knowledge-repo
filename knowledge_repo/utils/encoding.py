import sys

__all__ = ['encode', 'decode']


def encode(data, encoding='utf-8'):
    if sys.version_info.major == 2:
        if not isinstance(data, basestring):
            data = str(data)
    else:
        if not isinstance(data, str):
            data = str(data)
    if encoding is not None:
        if sys.version_info.major == 2:
            data = data.encode(encoding)
        else:
            data = bytes(data, encoding=encoding)
    return data


def decode(data, encoding='utf-8'):
    if encoding is not None:
        data = data.decode(encoding)
    return data
