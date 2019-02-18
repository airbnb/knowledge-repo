# -*- coding: utf-8 -*-
"""
    flask_sqlalchemy._compat
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Internal Python 2.x/3.x compatibility layer.

    :copyright: (c) 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE for more details.
"""
import sys

PY2 = sys.version_info[0] == 2


if PY2:
    def iteritems(d):
        return d.iteritems()

    def itervalues(d):
        return d.itervalues()

    xrange = xrange

    string_types = (unicode, bytes)

    def to_str(x, charset='utf8', errors='strict'):
        if x is None or isinstance(x, str):
            return x

        if isinstance(x, unicode):
            return x.encode(charset, errors)

        return str(x)

else:
    def iteritems(d):
        return iter(d.items())

    def itervalues(d):
        return iter(d.values())

    xrange = range

    string_types = (str,)

    def to_str(x, charset='utf8', errors='strict'):
        if x is None or isinstance(x, str):
            return x

        if isinstance(x, bytes):
            return x.decode(charset, errors)

        return str(x)
