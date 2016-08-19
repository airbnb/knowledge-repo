"""Parses request information.

Functions include:
    - check_user
    - from_request_get_user_info
    - from_request_get_feed_params
"""
import inflection
import hashlib
from flask import current_app

from ..app import db_session
from ..models import User


def check_user_exists(username):
    """Check is user exists, and add if not."""

    # check to see if the user in the users table
    user_obj = (db_session.query(User)
                .filter(User.username == username)
                .first())
    if not user_obj:
        # need to create the user object and add
        user_obj = User(username=username)
        db_session.add(user_obj)
        db_session.commit()
    return user_obj


def get_user_id(username):
    """
    Creates an integer user id from a username string

    This function is used when it is preferable to store a users id rather
    than username, usually for speed or privacy reasons
    """
    user_obj = (db_session.query(User)
                .filter(User.username == username)
                .first())
    if user_obj is not None:
        return user_obj.id
    return None


def from_request_get_user_info(request):  # TODO: In the future, simply return the User object
    """Given the request, return the username and id of the user."""
    username = current_app.config.get(
        'AUTH_USERNAME_DEFAULT') or 'knowledge_default'
    if current_app.config.get('AUTH_USERNAME_REQUEST_HEADER') is not None:
        username = request.headers.get(current_app.config.get(
            'AUTH_USERNAME_REQUEST_HEADER'), username)
    user_obj = check_user_exists(username)
    return username, user_obj.id


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
    username, user_id = from_request_get_user_info(request)
    feed_params["username"] = username
    feed_params["user_id"] = user_id

    user_obj = (db_session.query(User)
                          .filter(User.id == user_id)
                          .first())

    if user_obj:
        feed_params["subscriptions"] = user_obj.get_subscriptions
    return feed_params
