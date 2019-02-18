# -*- coding: utf-8 -*-

from .utils import validate_str
import re
import ipaddress
import json
import time


@validate_str
def isascii(value):
    """
    Return whether or not given value contains ASCII chars only. Empty string is valid.
    If the value contains ASCII chars only, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isascii('1234abcDEF')
        True

        >>> isascii('ｆｏｏbar')
        False

    :param value: string to validate ASCII chars
    """
    ascii_pattern = re.compile(r"^[\x00-\x7F]+$")
    return value == '' or bool(ascii_pattern.match(value))


@validate_str
def isprintascii(value):
    """
    Return whether or not given value contains printable ASCII chars only. Empty string is valid.
    If the value contains printable ASCII chars only, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isprintascii('1234abcDEF')
        True

        >>> isprintascii('ｆｏｏbar')
        False

    :param value: string to validate printable ASCII chars
    """
    print_ascii = re.compile(r"^[\x20-\x7E]+$")
    return value == '' or bool(print_ascii.match(value))


@validate_str
def isnonempty(value):
    """
    Return whether the value is not empty

    Examples::

        >>> isnonempty('a')
        True

        >>> isnonempty('')
        False

    :param value: string to validate whether value is not empty
    """
    return value != ''


@validate_str
def isbase64(value):
    """
    Return whether or not given value is base64 encoded.
    If the value is base64 encoded, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isbase64('U3VzcGVuZGlzc2UgbGVjdHVzIGxlbw==')
        True

        >>> isbase64('Vml2YW11cyBmZXJtZtesting123')
        False

    :param value: string to validate base64 encoding
    """
    base64 = re.compile(r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$")
    return bool(base64.match(value))


@validate_str
def isemail(value):
    """
    Return whether or not given value is an email.
    If the value is an email, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isemail('foo@bar.com')
        True

        >>> isemail('invalidemail@')
        False

    :param value: string to validate email
    """
    email = re.compile(r"""^(((([a-zA-Z]|\d|[!#$%&'*+\-/=?^_`{|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-zA-Z]|\d|[!#$%&'*+\-/=?^_`{|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-zA-Z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-zA-Z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-zA-Z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-zA-Z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-zA-Z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-zA-Z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-zA-Z]|\d|-|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-zA-Z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$""")
    return bool(email.match(value))


@validate_str
def ishexadecimal(value):
    """
    Return whether or not given value is a hexadecimal number.
    If the value is a hexadecimal number, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> ishexadecimal('deadBEEF')
        True

        >>> ishexadecimal('abcdefg')
        False

    :param value: string to validate hexadecimal number
    """
    try:
        return int(value, 16) >= 0
    except ValueError:
        return False


@validate_str
def ishexcolor(value):
    """
    Return whether or not given value is a hexadecimal color.
    If the value is a hexadecimal color, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> ishexcolor('#ff0034')
        True

        >>> ishexcolor('#ff12FG')
        False

    :param value: string to validate hexadecimal color
    """
    value = value.lstrip('#')
    try:
        return int(value, 16) >= 0 and len(value) in (3, 6)
    except ValueError:
        return False


@validate_str
def isrgbcolor(value):
    """
    Return whether or not given value is a rgb color.
    If the value is a rgb color, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isrgbcolor('rgb(0,31,255)')
        True

        >>> isrgbcolor('rgb(1,349,275)')
        False

    :param value: string to validate rgb color
    """
    rgb = re.compile(r"^rgb\(\s*(0|[1-9]\d?|1\d\d?|2[0-4]\d|25[0-5])\s*,\s*(0|[1-9]\d?|1\d\d?|2[0-4]\d|25[0-5])\s*,\s*(0|[1-9]\d?|1\d\d?|2[0-4]\d|25[0-5])\s*\)$")
    return bool(rgb.match(value))


@validate_str
def isint(value):
    """
    Return whether or not given value is an integer.
    If the value is an integer, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isint('-2147483648')
        True

        >>> isint('123.123')
        False

    :param value: string to validate integer
    """
    integer = re.compile(r"^(?:[-+]?(?:0|[1-9][0-9]*))$")
    return value != '' and bool(integer.match(value))


@validate_str
def isfloat(value):
    """
    Return whether or not given value is a float.
    This does not give the same answer as::

        isinstance(num_value,float)

    Because isfloat('1') returns true.  More strict typing requirements may want
    to use is_instance.

    If the value is a float, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isfloat('01.123')
        True

        >>> isfloat('+1f')
        False

    :param value: string to validate float
    """
    floating = re.compile(r"^(?:[-+]?(?:[0-9]+))?(?:\.[0-9]*)?(?:[eE][+\-]?(?:[0-9]+))?$")
    return value != '' and bool(floating.match(value))


@validate_str
def ispositive(value):
    """
    Return whether a number is positive or not

    Examples::

        >>> ispositive('1')
        True

        >>> ispositive('1.')
        True

        >>> ispositive('-1.')
        False

        >>> ispositive('a')
        False

    :param value: string to validate number
    """
    if not isfloat(value):
        return False
    return float(value) > 0


@validate_str
def isslug(value):
    """
    Validate whether or not given value is valid slug.
    Valid slug can contain only alphanumeric characters, hyphens and
    underscores. If the value is a slug, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isslug('my-slug-2134')
        True

        >>> isslug('my.slug')
        False

    :param value: value to validate
    """
    slug = re.compile(r'^[-a-zA-Z0-9_]+$')
    return bool(slug.match(value))


@validate_str
def isuuid(value):
    """
    Return whether or not given value is a UUID (version 3, 4 or 5).
    If the value is a UUID (version 3, 4 or 5), this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isuuid('a987fbc9-4bed-3078-cf07-9141ba07c9f3')
        True

        >>> isuuid('xxxA987FBC9-4BED-3078-CF07-9141BA07C9F3')
        False

    :param value: string to validate UUID (version 3, 4 or 5)
    """
    uuid = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
    return bool(uuid.match(value))


@validate_str
def isuuid3(value):
    """
    Return whether or not given value is a UUID version 3.
    If the value is a UUID version 3, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isuuid3('A987FBC9-4BED-3078-CF07-9141BA07C9F3')
        True

        >>> isuuid3('xxxA987FBC9-4BED-3078-CF07-9141BA07C9F3')
        False

    :param value: string to validate UUID version 3
    """
    uuid3 = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-3[0-9a-fA-F]{3}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
    return bool(uuid3.match(value))


@validate_str
def isuuid4(value):
    """
    Return whether or not given value is a UUID version 4.
    If the value is a UUID version 4, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isuuid4('713ae7e3-cb32-45f9-adcb-7c4fa86b90c1')
        True

        >>> isuuid4('A987FBC9-4BED-3078-CF07-9141BA07C9F3')
        False

    :param value: string to validate UUID version 4
    """
    uuid4 = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
    return bool(uuid4.match(value))


@validate_str
def isuuid5(value):
    """
    Return whether or not given value is a UUID version 5.
    If the value is a UUID version 5, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isuuid5('987FBC97-4BED-5078-AF07-9141BA07C9F3')
        True

        >>> isuuid5('9c858901-8a57-4791-81fe-4c455b099bc9')
        False

    :param value: string to validate UUID version 5
    """
    uuid5 = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-5[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
    return bool(uuid5.match(value))


@validate_str
def isfullwidth(value):
    """
    Return whether or not given value contains any full-width chars.
    If the value contains any full-width chars, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isfullwidth('３ー０　ａ＠ｃｏｍ')
        True

        >>> isfullwidth('abc123')
        False

    :param value: string to validate full-width chars
    """
    full = re.compile(r"[^\u0020-\u007E\uFF61-\uFF9F\uFFA0-\uFFDC\uFFE8-\uFFEE0-9a-zA-Z]")
    return bool(full.match(value))


@validate_str
def ishalfwidth(value):
    """
    Return whether or not given value contains any half-width chars.
    If the value contains any half-width chars, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> ishalfwidth('l-btn_02--active')
        True

        >>> ishalfwidth('００１１')
        False

    :param value: string to validate half-width chars
    """
    half = re.compile(r"[\u0020-\u007E\uFF61-\uFF9F\uFFA0-\uFFDC\uFFE8-\uFFEE0-9a-zA-Z]")
    return bool(half.match(value))


@validate_str
def islatitude(value):
    """
    Return whether or not given value is valid latitude.
    If the value is valid latitude, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> islatitude('-90.000')
        True

        >>> islatitude('+99.9')
        False

    :param value: string to validate latitude
    """
    lat = re.compile(r'^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)$')
    return bool(lat.match(value))


@validate_str
def islongitude(value):
    """
    Return whether or not given value is valid longitude.
    If the value is valid longitude, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> islongitude('+73.234')
        True

        >>> islongitude('180.1')
        False

    :param value: string to validate longitude
    """
    long = re.compile(r'^[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$')
    return bool(long.match(value))


@validate_str
def ismac(value):
    """
    Return whether or not given value is valid MAC address.
    If the value is valid MAC address, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> ismac('3D:F2:C9:A6:B3:4F')
        True

        >>> ismac('01:02:03:04:05')
        False

    :param value: string to validate MAC address
    """
    mac = re.compile(r'^([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])$')
    return bool(mac.match(value))


@validate_str
def ismd5(value):
    """
    Return whether or not given value is MD5 encoded.
    If the value is MD5 encoded, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> ismd5('d94f3f016ae679c3008de268209132f2')
        True

        >>> ismd5('KYT0bf1c35032a71a14c2f719e5a14c1')
        False

    :param value: string to validate MD5 encoding
    """
    return ishexadecimal(value) and len(value) == 32


@validate_str
def issha1(value):
    """
    Return whether or not given value is SHA1 encoded.
    If the value is SHA1 encoded, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> issha1('1bc6b8a58b484bdb6aa5264dc554934e3e46c405')
        True

        >>> issha1('ZKYT059dbf1c356032a7b1a1d4c2f719e5a14c1')
        False

    :param value: string to validate SHA1 encoding
    """
    return ishexadecimal(value) and len(value) == 40


@validate_str
def issha256(value):
    """
    Return whether or not given value is SHA256 encoded.
    If the value is SHA256 encoded, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> issha256('fd04c4a99b6b1f118452da33dfe9523ec164f5fecde4502b69f1ed3f24a29ff6')
        True

        >>> issha256('KLO4545ID55545789Hg545235F4525576adca7676cd7dca7976676e6789dcaee')
        False

    :param value: string to validate SHA256 encoding
    """
    return ishexadecimal(value) and len(value) == 64


@validate_str
def issha512(value):
    """
    Return whether or not given value is SHA512 encoded.
    If the value is SHA512 encoded, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> issha512('0b696861da778f6bd0d899ad9a581f4b9b1eb8286eaba266d2f2e2767539055bf8eb59e8884839a268141aba1ef078ce67cf94d421bd1195a3c0e817f5f7b286')
        True

        >>> issha512('KLO4545ID55545789Hg545235F45255452Hgf76DJF56HgKJfg3456356356346534534653456sghey45656jhgjfgghdfhgdfhdfhdfhdfhghhq94375dj93458w34')
        False

    :param value: string to validate SHA512 encoding
    """
    return ishexadecimal(value) and len(value) == 128


@validate_str
def ismongoid(value):
    """
    Return whether or not given value is a valid hex-encoded representation of a MongoDB ObjectId.
    If the value is a MongoDB ObjectId, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> ismongoid('507f1f77bcf86cd799439011')
        True

        >>> ismongoid('507f1f77bcf86cd7994390')
        False

    :param value: string to validate MongoDB ObjectId
    """
    return ishexadecimal(value) and len(value) == 24


@validate_str
def isiso8601(value):
    """
    Return whether or not given value is ISO 8601 date.
    If the value is ISO 8601 date, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isiso8601('2009-12T12:34')
        True

        >>> isiso8601('2009367')
        False

    :param value: string to validate ISO 8601 date
    """
    iso8601 = re.compile(r'^([+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24:?00)([.,]\d+(?!:))?)?(\17[0-5]\d([.,]\d+)?)?([zZ]|([+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$')
    return bool(iso8601.match(value))


@validate_str
def isipv4(value):
    """
    Return whether or not given value is an IP version 4.
    If the value is an IP version 4, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isipv4('127.0.0.1')
        True

        >>> isipv4('::1')
        False

    :param value: string to validate IP version 4
    """
    try:
        ip_addr = ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError:
        return False
    return ip_addr.version == 4


@validate_str
def isipv6(value):
    """
    Return whether or not given value is an IP version 6.
    If the value is an IP version 6, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isipv6('2001:41d0:2:a141::1')
        True

        >>> isipv6('127.0.0.1')
        False

    :param value: string to validate IP version 6
    """
    try:
        ip_addr = ipaddress.IPv6Address(value)
    except ipaddress.AddressValueError:
        return False
    return ip_addr.version == 6


@validate_str
def isip(value):
    """
    Return whether or not given value is an IP version 4 or 6.
    If the value is an IP version 4 or 6, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isip('127.0.0.1')
        True

        >>> isip('0200.200.200.200')
        False

    :param value: string to validate IP version 4 or 6
    """
    return isipv4(value) or isipv6(value)


@validate_str
def isport(value):
    """
    Return whether or not given value represents a valid port.
    If the value represents a valid port, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isport('8080')
        True

        >>> isport('65536')
        False

    :param value: string to validate port
    """
    try:
        return 0 < int(value) < 65536
    except ValueError:
        return False


@validate_str
def isdns(value):
    """
    Return whether or not given value represents a valid DNS name.
    If the value represents a valid DNS name, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isdns('localhost')
        True

        >>> isdns('a.b..')
        False

    :param value: string to validate DNS name
    """
    dns = re.compile(r'^([a-zA-Z0-9_][a-zA-Z0-9_-]{0,62})(\.[a-zA-Z0-9_][a-zA-Z0-9_-]{0,62})*[._]?$')
    if value == '' or len(value.replace('.', '')) > 255:
        return False
    return (not isip(value)) and bool(dns.match(value))


@validate_str
def isssn(value):
    """
    Return whether or not given value is a U.S. Social Security Number.
    If the value is a U.S. Social Security Number, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isssn('191 60 2869')
        True

        >>> isssn('66690-76')
        False

    :param value: string to validate U.S. Social Security Number
    """
    ssn = re.compile(r'^\d{3}[- ]?\d{2}[- ]?\d{4}$')
    if value == '' or len(value) != 11:
        return False
    return bool(ssn.match(value))


@validate_str
def issemver(value):
    """
    Return whether or not given value is valid semantic version.
    If the value is valid semantic version, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> issemver('v1.0.0')
        True

        >>> issemver('1.1.01')
        False

    :param value: string to validate semantic version
    """
    semver = re.compile(r'^v?(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(-(0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(\.(0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*)?(\+[0-9a-zA-Z-]+(\.[0-9a-zA-Z-]+)*)?$')
    return bool(semver.match(value))


@validate_str
def isbytelen(value, minimum, maximum):
    """
    Return whether or not given value's length (in bytes) falls in a range.
    If the value's length (in bytes) falls in a range, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isbytelen('123456', 0, 100)
        True

        >>> isbytelen('1239999', 0, 1)
        False

    :param value: string to validate length (in bytes) falls in a range
    :param minimum: minimum value of the range in integer
    :param maximum: maximum value of the range in integer
    """
    return minimum <= len(value) <= maximum


@validate_str
def ismultibyte(value):
    """
    Return whether or not given value contains one or more multibyte chars.
    If the value contains one or more multibyte chars, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> ismultibyte('あいうえお foobar')
        True

        >>> ismultibyte('abc')
        False

    :param value: string to validate one or more multibyte chars
    """
    multi_byte = re.compile(r"[^\x00-\x7F]")
    return bool(multi_byte.match(value))


@validate_str
def isfilepath(value):
    """
    Return whether or not given value is Win or Unix file path and returns it's type.
    If the value is Win or Unix file path, this function returns ``True, Type``, otherwise ``False, Type``.

    Examples::

        >>> isfilepath('c:\\path\\file (x86)\\bar')
        True, 'Win'

        >>> isfilepath('/path')
        True, 'Unix'

        >>> isfilepath('c:/path/file/')
        False, 'Unknown'

    :param value: string to validate file path
    """
    win_path = re.compile(r'^[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$')
    nix_path = re.compile(r'^(/[^/\x00]*)+/?$')
    if win_path.match(value):
        # check windows path limit see:
        # http://msdn.microsoft.com/en-us/library/aa365247(VS.85).aspx#maxpath
        if len(value[3:]) > 32767:
            return False, 'Win'
        return True, 'Win'
    elif nix_path.match(value):
        return True, 'Unix'
    return False, 'Unknown'


@validate_str
def isdatauri(value):
    """
    Return whether or not given value is base64 encoded data URI such as an image.
    If the value is base64 encoded data URI, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isdatauri('data:text/plain;base64,Vml2YW11cyBmZXJtZW50dW0gc2VtcGVyIHBvcnRhLg==')
        True

        >>> isdatauri('dataxbase64data:HelloWorld')
        False

    :param value: string to validate base64 encoded data URI
    """
    data_uri = re.compile(r"\s*data:([a-zA-Z]+/[a-zA-Z0-9\-+]+(;[a-zA-Z\-]+=[a-zA-Z0-9\-]+)?)?(;base64)?,[a-zA-Z0-9!$&',()*+,;=\-._~:@/?%\s]*\s*$")
    return bool(data_uri.match(value))


@validate_str
def isjson(value):
    """
    Return whether or not given value is valid JSON.
    If the value is valid JSON, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isjson('{"Key": {"Key": {"Key": 123}}}')
        True

        >>> isjson('{ key: "value" }')
        False

    :param value: string to validate JSON
    """
    try:
        decoded_json = json.loads(value)
    except ValueError:
        return False
    return True


@validate_str
def istime(value, fmt):
    """
    Return whether or not given value is valid time according to given format.
    If the value is valid time, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> istime('30 Nov 00', '%d %b %y')
        True

        >>> istime('Friday', '%d')
        False

    :param value: string to validate time
    :param fmt: format of time
    """
    try:
        time_obj = time.strptime(value, fmt)
    except ValueError:
        return False
    return True


@validate_str
def isurl(value):
    """
    Return whether or not given value is an URL.
    If the value is an URL, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isurl('http://foo.bar#com')
        True

        >>> isurl('http://foobar.c_o_m')
        False

    :param value: string to validate URL
    """
    # Regex patterns for validating URL is taken from
    # Django's URLValidator class

    ul = '\u00a1-\uffff'

    # IP patterns
    ipv4_re = r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
    ipv6_re = r'\[[0-9a-f:\.]+\]'

    # Host patterns
    hostname_re = r'[a-z' + ul + r'0-9](?:[a-z' + ul + r'0-9-]{0,61}[a-z' + ul + r'0-9])?'
    domain_re = r'(?:\.(?!-)[a-z' + ul + r'0-9-]{1,63}(?<!-))*'
    tld_re = r'\.(?!-)(?:[a-z' + ul + '-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)\.?'  # may have a trailing dot
    host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'
    url = re.compile(r'^(ftp|tcp|rtmp|udp|wss?|https?)://(?:\S+(?::\S*)?@)?(?:' + ipv4_re + '|' + ipv6_re + '|' + host_re + ')(?::\d{2,5})?(?:[/?#][^\s]*)?\Z', re.IGNORECASE)

    if value == '' or len(value) >= 2083 or len(value) <= 3:
        return False
    return bool(url.match(value))


@validate_str
def iscrcard(value):
    """
    Return whether or not given value is a credit card.
    If the value is a credit card, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> iscrcard('375556917985515')
        True

        >>> iscrcard('5398228707871528')
        False

    :param value: string to validate credit card
    """
    pattern = re.compile(r"^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})$")
    sanitized = re.sub(r'[^0-9]+', '', value)
    if not pattern.match(sanitized):
        return False
    summation = 0
    should_double = False
    for i in reversed(range(len(sanitized))):
        digit = int(sanitized[i:i+1])
        if should_double:
            digit *= 2
            if digit >= 10:
                summation += (digit % 10) + 1
            else:
                summation += digit
        else:
            summation += digit
        should_double = not should_double
    if summation % 10 == 0:
        return True
    return False


@validate_str
def isisin(value):
    """
    Return whether or not given value is valid International Securities Identification Number.
    If the value is a valid ISIN, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isisin('AU0000XVGZA3')
        True

        >>> isisin('DE000BAY0018')
        False

    :param value: string to validate ISIN
    """
    pattern = re.compile(r'^[A-Z]{2}[0-9A-Z]{9}[0-9]$')
    if not pattern.match(value):
        return False

    checksum_str = re.sub(r'[A-Z]', lambda ch: str(int(ch.group(0), 36)), value)
    summation = 0
    should_double = True
    for i in checksum_str[-2::-1]:
        digit = int(i)
        if should_double:
            digit *= 2
            if digit >= 10:
                summation += (digit + 1)
            else:
                summation += digit
        else:
            summation += digit
        should_double = not should_double

    return int(value[-1]) == (10000 - summation) % 10


@validate_str
def isiban(value):
    """
    Return whether or not given value is a valid IBAN code.
    If the value is a valid IBAN, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isiban('DE29100500001061045672')
        True

        >>> isiban('NO9186011117947')
        False

    :param value: string to validate IBAN code
    """
    pattern = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}$')
    cleaned_value = value.replace(' ', '').replace('\t', '')
    iban = cleaned_value[4:] + cleaned_value[:4]
    if not pattern.match(cleaned_value):
        return False
    digits = int(''.join(str(int(ch, 36)) for ch in iban))  # BASE 36: 0..9,A..Z -> 0..35
    return digits % 97 == 1


@validate_str
def isimei(value):
    """
    Return whether or not given value is an imei.
    If the value is an imei, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isimei('565464561111118')
        True

        >>> isimei('123456789012341')
        False

    :param value: string to validate imei
    """
    pattern = re.compile(r'^[0-9]{15}$')
    sanitized = re.sub(r'[ -]', '', value)
    if not pattern.match(sanitized):
        return False

    should_double = True
    total_sum = 0
    for digit in reversed(sanitized[:-1]):
        digit_int = int(digit)
        if should_double:
            digit_int = digit_int * 2

        if digit_int >= 10:
            total_sum += (digit_int - 9)
        else:
            total_sum += digit_int
        should_double = not should_double
    if str(10 - (total_sum % 10))[-1] == sanitized[-1]:
        return True
    else:
        return False


@validate_str
def ismimetype(value):
    """
    Checks if the provided string matches to a correct Media type format (MIME type)
    If the value is a valid MIME Type, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> ismimetype('application/xhtml+xml')
        True

        >>> ismimetype('application/json/text')
        False

    :param value: string to validate MIME Type
    """
    simple = re.compile(r'^(application|audio|font|image|message|model|multipart|text|video)/[a-zA-Z0-9.\-+]{1,100}$', re.IGNORECASE)
    text = re.compile(r'^text/[a-zA-Z0-9.\-+]{1,100};\s?charset=("[a-zA-Z0-9.\-+\s]{0,70}"|[a-zA-Z0-9.\-+]{0,70})(\s?\([a-zA-Z0-9.\-+\s]{1,20}\))?$', re.IGNORECASE)
    multipart = re.compile(r'^multipart/[a-zA-Z0-9.\-+]{1,100}(;\s?(boundary|charset)=("[a-zA-Z0-9.\-+\s]{0,70}"|[a-zA-Z0-9.\-+]{0,70})(\s?\([a-zA-Z0-9.\-+\s]{1,20}\))?){0,2}$', re.IGNORECASE)
    return bool(simple.match(value) or text.match(value) or multipart.match(value))


@validate_str
def isisrc(value):
    """
    Checks if the provided string is valid ISRC(International Standard Recording Code)
    If the value is a valid ISRC, this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isisrc('USAT29900609')
        True

        >>> isisrc('USAT2990060')
        False

    :param value: string to validate MIME Type
    """
    isrc = re.compile(r'^[A-Z]{2}[0-9A-Z]{3}\d{2}\d{5}$')
    return bool(isrc.match(value))
