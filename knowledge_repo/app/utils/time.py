import datetime


def time_since(dt, human_readable=False):
    if dt is None:
        return None
    assert isinstance(dt, datetime.datetime)
    delta = (datetime.datetime.utcnow() - dt).total_seconds()
    if human_readable:
        return human_readable_time_delta(delta)
    return delta


def human_readable_time_delta(seconds):
    if seconds is None:
        return "Never"
    elif seconds < 60:
        return "{:d} seconds ago".format(int(round(seconds)))
    elif seconds < 60 * 60:
        return "{:d} minutes ago".format(int(round(seconds / 60)))
    elif seconds < 24 * 60 * 60:
        return "{:d} hours ago".format(int(round(seconds / 60 / 60)))
    else:
        return "{:d} days ago".format(int(round(seconds / 60 / 60 / 24)))
