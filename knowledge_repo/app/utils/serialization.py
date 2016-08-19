import json

from sqlalchemy.orm import class_mapper


def class_to_dict(model):
    """Transforms a model into a dictionary which can be dumped to JSON."""
    # first we get the names of all the columns on your model
    columns = [c.key for c in class_mapper(model.__class__).columns]
    # then we return their values in a dict
    return dict((c, getattr(model, c)) for c in columns)


def to_json(inp):
    """Transforms a model into a dictionary which can be dumped to JSON."""
    if type(inp) == list:
        return json.dumps([class_to_dict(cls) for cls in inp])
    else:
        return json.dumps(class_to_dict(inp))
