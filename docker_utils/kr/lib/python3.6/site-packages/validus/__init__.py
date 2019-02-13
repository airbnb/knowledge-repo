# -*- coding: utf-8 -*-

import sys
if sys.version_info[0] < 3:
    sys.exit('Sorry, Python < 3 is not supported')

__author__ = """Rafiqul Hasan"""
__email__ = 'shopnilsazal@gmail.com'
__version__ = '0.2.0'


from .phones import isphone
from .isbn import isisbn, isisbn10, isisbn13
from .validators import isascii, isprintascii, isbase64, isemail, ishexadecimal
from .validators import isint, isfloat, ispositive, isslug, isnonempty
from .validators import isuuid, isuuid3, isuuid4, isuuid5
from .validators import isfullwidth, ishalfwidth, islatitude, islongitude
from .validators import ismac, ismd5, ismongoid, isiso8601, isbytelen
from .validators import isipv4, isipv6, isip, isport, isdns, isssn, issemver
from .validators import ismultibyte, isfilepath, isdatauri, isjson, istime, isurl
from .validators import iscrcard, isisin, isiban, ishexcolor, isrgbcolor, isimei
from .validators import issha1, issha256, issha512, ismimetype, isisrc
