"""Parses request information.

Functions include:
    - check_user
    - from_request_get_user_info
    - from_request_get_feed_params
"""
import inflection
from flask import g

from ..app import db_session
from ..models import User


def from_request_get_feed_params(request):
    """Given the request, return an object that contains the parameters.

    :param request: The request obj
    :type request: Flask request
    :return: Select parameters passed in through headers or the url
    :rtype: object
    """

    feed_params = {}

    feed_params["filters"] = request.args.get('filters')
    feed_params["authors"] = request.args.get('authors')
    feed_params["start"] = int(request.args.get('start', 0))
    feed_params["results"] = int(request.args.get('results', 10))
    feed_params["sort_by"] = inflection.underscore(
        request.args.get('sort_by', 'updated_at'))
    feed_params["sort_desc"] = not bool(request.args.get('sort_asc', ''))
    username, user_id = g.user.username, g.user.id
    feed_params["username"] = username
    feed_params["user_id"] = user_id

    user_obj = (db_session.query(User)
                          .filter(User.id == user_id)
                          .first())

    if user_obj:
        feed_params["subscriptions"] = user_obj.get_subscriptions
    return feed_params
