# -*- coding: utf-8 -*-
"""
Python Markdown

A Python implementation of John Gruber's Markdown.

Documentation: https://python-markdown.github.io/
GitHub: https://github.com/Python-Markdown/markdown/
PyPI: https://pypi.org/project/Markdown/

Started by Manfred Stienstra (http://www.dwerg.net/).
Maintained for a few years by Yuri Takhteyev (http://www.freewisdom.org).
Currently maintained by Waylan Limberg (https://github.com/waylan),
Dmitry Shachnev (https://github.com/mitya57) and Isaac Muse (https://github.com/facelessuser).

Copyright 2007-2018 The Python Markdown Project (v. 1.7 and later)
Copyright 2004, 2005, 2006 Yuri Takhteyev (v. 0.2-1.6b)
Copyright 2004 Manfred Stienstra (the original version)

License: BSD (see LICENSE.md for details).
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from .core import Markdown, markdown, markdownFromFile

# For backward compatibility as some extensions expect it...
from .extensions import Extension  # noqa

__all__ = ['Markdown', 'markdown', 'markdownFromFile']

# version_info should conform to PEP 386
# (major, minor, micro, alpha/beta/rc/final, #)
# (1, 1, 2, 'alpha', 0) => "1.1.2.dev"
# (1, 2, 0, 'beta', 2) => "1.2b2"
__version_info__ = (3, 0, 1, 'final', 0)


def _get_version():  # pragma: no cover
    " Returns a PEP 386-compliant version number from version_info. "
    assert len(__version_info__) == 5
    assert __version_info__[3] in ('alpha', 'beta', 'rc', 'final')

    parts = 2 if __version_info__[2] == 0 else 3
    main = '.'.join(map(str, __version_info__[:parts]))

    sub = ''
    if __version_info__[3] == 'alpha' and __version_info__[4] == 0:
        # TODO: maybe append some sort of git info here??
        sub = '.dev'
    elif __version_info__[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[__version_info__[3]] + str(__version_info__[4])

    return str(main + sub)


__version__ = _get_version()

# Also support `version` for backward-compatabillity with <3.0 versions
version_info = __version_info__
version = __version__
