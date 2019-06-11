"""Parses request information.

Functions include:
    - check_user
    - from_request_get_user_info
    - from_url_get_feed_params
"""
import inflection
from flask import g

from ..proxies import db_session
from ..models import User
from ..proxies import current_user


def from_url_get_feed_params(url):
    """Given the request, return an object that contains the parameters.

    :param request: The request obj
    :type request: Flask request
    :return: Select parameters passed in through headers or the url
    :rtype: object
    """

    feed_params = {'kr': None, 'filters': None, 'authors': None, 'start': 0, 'results': 10, 'sort_by': 'updated_at', 'sort_desc': True}
    # default values of all filters if they are not present in url

    qidx = url.find('?')
    posts = []
    if qidx != -1:
      url_search = url[qidx+1:]
      url_search_arr = url_search.split('&')
      for filter in url_search_arr:
        query, val = filter.split('=')
        if '%2F' in val:
          val=val.split('%2F')
          val=val[0]+'/'+val[1]
        feed_params[query] = val

      
    username, user_id = current_user.identifier, current_user.id
    feed_params["username"] = username
    feed_params["user_id"] = user_id

    user_obj = (db_session.query(User)
                          .filter(User.id == user_id)
                          .first())

    if user_obj:
        feed_params["subscriptions"] = user_obj.subscriptions
    return feed_params
