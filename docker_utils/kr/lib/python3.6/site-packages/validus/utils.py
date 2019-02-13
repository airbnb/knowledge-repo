from functools import wraps


def validate_str(func):
    """
    A decorator function to validate if the input is string
    :param func: a function to validate
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if isinstance(args[0], str):
            return func(*args, **kwargs)
        else:
            raise TypeError('It only supports string validation.')
    return wrapper

