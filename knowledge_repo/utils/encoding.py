import os
import sys
import logging

from future.utils import raise_with_traceback

__all__ = ['encode', 'decode']

logger = logging.getLogger(__name__)


def encode(data, encoding='utf-8'):
    assert encoding == 'utf-8', "Only UTF-8 encoding is currently supported."
    # Check if data is alreqdy encoded (for the purposes of unicode only
    # If not, convert to a string if necessary, and then encode as utf-8 bytes
    if sys.version_info.major == 2:
        if not isinstance(data, basestring):
            data = unicode(data)
        elif not isinstance(data, unicode):
            return data  # UTF-8 data is already encoded
    else:
        if isinstance(data, bytes):
            return data  # UTF-8 data is already encoded
        elif not isinstance(data, str):
            data = str(data)
    # Encode UTF-8 data
    if encoding is not None:
        try:
            data = data.encode(encoding)
        except Exception as e:
            if os.environ.get('DEBUG'):
                raise_with_traceback(e)
            logger.warning("An encoding error has occurred... continuing anyway. To capture these errors, rerun the current command prefixed with `DEBUG=1 `.")
            data = data.encode(encoding, errors='ignore')
    return data


def decode(data, encoding='utf-8'):
    assert encoding == 'utf-8', "Only UTF-8 encoding is currently supported."
    if encoding is not None:
        try:
            data = data.decode(encoding)
        except Exception as e:
            if os.environ.get('DEBUG'):
                raise_with_traceback(e)
            logger.warning("An decoding error has occurred... continuing anyway. To capture these errors, rerun the current command prefixed with `DEBUG=1 `.")
            data = data.decode(encoding, errors='ignore')
    return data
