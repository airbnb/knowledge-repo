""" Define the routes that enable like/unlike on posts.

This includes:
  - /like
  - /unlike
"""
import logging
from flask import request, Blueprint, current_app
from sqlalchemy import and_

from ..app import db_session
from ..models import Post, Vote, PageView
from ..utils.requests import from_request_get_user_info


blueprint = Blueprint(
    'vote', __name__, template_folder='../templates', static_folder='../static')


@blueprint.route('/like')
@PageView.log_pageview
def render_likes():
    """ Like a post """
    try:
        path = request.args.get('post_id', '')  # This will prevent old code from adding invalid post_ids
        if path == '':
            return "No Post Found to Unlike!"
        username, user_id = from_request_get_user_info(request)
        post_id = (db_session.query(Post)
                             .filter(Post.path == path)
                             .first()).id
        vote = (db_session.query(Vote)
                .filter(and_(Vote.object_id == post_id, Vote.user_id == user_id))
                .first())
        if not vote:
            vote = Vote(user_id=user_id, object_id=post_id)
            db_session.add(vote)
            db_session.commit()
    except:
        logging.warning("ERROR processing request")
    return ""


@blueprint.route('/unlike')
@PageView.log_pageview
def render_unlikes():
    """ Un-like a post """
    try:
        path = request.args.get('post_id', '')  # This will prevent old code from adding invalid post_ids
        if path == '':
            return "No Post Found to Unlike!"
        username, user_id = from_request_get_user_info(request)
        post_id = (db_session.query(Post)
                             .filter(Post.path == path)
                             .first()).id
        votes = (db_session.query(Vote)
                 .filter(and_(Vote.object_id == post_id, Vote.user_id == user_id))
                 .all())
        if votes:
            for vote in votes:
                db_session.delete(vote)
            db_session.commit()
    except:
        logging.warning("ERROR processing request")
    return ""
