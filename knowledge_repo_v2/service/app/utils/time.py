from datetime import datetime


def time_since(dt, human_readable=False, default=None):
    if dt is None:
        return default
    assert isinstance(dt, datetime)
    delta = (datetime.utcnow() - dt).total_seconds()
    if human_readable:
        return human_readable_time_delta(delta)
    return delta


def human_readable_time_delta(seconds):
    if seconds is None:
        return "Never"
    elif seconds < 60:
        return f'{seconds:.0f} seconds ago'
    elif seconds < 60 * 60:
        return f'{(seconds / 60):.0f} minutes ago'
    elif seconds < 24 * 60 * 60:
        return f'{(seconds / 60 / 60):.0f} hours ago'
    else:
        return f'{(seconds / 60 / 60 / 24):.0f} days ago'
