from flask import current_app

from ..app import db_session
from ..constants import TagConstants
from ..models import Tag


def get_tag_ids(tags):
    tag_ids = []
    for tag in tags:
        if tag[0] == "#":
            tag = tag[1:]
        tag_obj = Tag(name=tag)
        tag_ids.append(tag_obj.id)
    return tag_ids
