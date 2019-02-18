from .utils import validate_str
import re


@validate_str
def sanitize_isbn(isbn):
    sanitized = re.sub(r'[\s-]+', '', isbn)
    return sanitized


def get_isbn_10_checksum(isbn):
    sanitized = sanitize_isbn(isbn)
    checksum = sum([(i+1) * int(sanitized[i]) for i in range(9)])
    if sanitized[9] == 'X':
        checksum += 10 * 10
    else:
        checksum += 10 * int(sanitized[9])
    return checksum


def get_isbn_13_checksum(isbn):
    sanitized = sanitize_isbn(isbn)
    factor = [1, 3]
    checksum = sum([factor[i % 2] * int(sanitized[i]) for i in range(12)])
    return checksum


def isisbn(isbn, version=None):
    """
    Return whether or not given value is a valid ISBN (version 10 or 13).
    If version value is not equal to 10 or 13, it will be check both variants.
    If the value is a valid ISBN this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isisbn('978-3-8362-2119-1')
        True

        >>> isisbn('978-3-8362-2119-0')
        False

    :param isbn: ISBN string to validate
    :param version: Optional ISBN version (10 or 13)
    """
    isbn10_pattern = re.compile(r"^(?:[0-9]{9}X|[0-9]{10})$")
    isbn13_pattern = re.compile(r"^(?:[0-9]{13})$")
    sanitized = sanitize_isbn(isbn)

    if version == 10:
        if not isbn10_pattern.match(sanitized):
            return False
        checksum = get_isbn_10_checksum(isbn)
        if checksum % 11 == 0:
            return True
        return False

    elif version == 13:
        if not isbn13_pattern.match(sanitized):
            return False
        checksum = get_isbn_13_checksum(isbn)
        if int(sanitized[12]) - ((10 - (checksum % 10)) % 10) == 0:
            return True
        return False

    return isisbn(isbn, 10) or isisbn(isbn, 13)


def isisbn10(isbn):
    """
    Return whether or not given value is a valid ISBN version 10.
    If the value is a valid ISBN version 10 this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isisbn10('3-401-01319-X')
        True

        >>> isisbn10('3-423-21412-1')
        False

    :param isbn: ISBN version 10 string to validate
    """
    return isisbn(isbn, 10)


def isisbn13(isbn):
    """
    Return whether or not given value is a valid ISBN version 13.
    If the value is a valid ISBN version 13 this function returns ``True``, otherwise ``False``.

    Examples::

        >>> isisbn13('978-4-87311-368-5')
        True

        >>> isisbn13('01234567890ab')
        False

    :param isbn: ISBN version 13 string to validate
    """
    return isisbn(isbn, 13)

