""" Define the routes that enable like/unlike on posts.

This includes:
  - /like
  - /unlike
"""
import logging
from flask import request, Blueprint, g
from flask_login import login_required
from sqlalchemy import and_

from ..proxies import db_session
from ..models import Post, Vote, PageView
from ..proxies import current_user


blueprint = Blueprint(
    'vote', __name__, template_folder='../templates', static_folder='../static')


@blueprint.route('/like')
@PageView.logged
@login_required
def like_post():
    """ Like a post """
    try:
        post_id = int(request.args.get('post_id', '-1'))  # This will prevent old code from adding invalid post_ids
        if post_id < 0:
            return "No Post Found to like!"
        vote = (db_session.query(Vote)
                .filter(and_(Vote.object_id == post_id, Vote.user_id == current_user.id))
                .first())
        if not vote:
            vote = Vote(user_id=current_user.id, object_id=post_id)
            db_session.add(vote)
            db_session.commit()
    except:
        logging.warning("ERROR processing request")
    return ""


@blueprint.route('/unlike')
@PageView.logged
@login_required
def unlike_post():
    """ Un-like a post """
    try:
        post_id = int(request.args.get('post_id', '-1'))  # This will prevent old code from adding invalid post_ids
        if post_id < 0:
            return "No Post Found to Unlike!"
        votes = (db_session.query(Vote)
                 .filter(and_(Vote.object_id == post_id, Vote.user_id == current_user.id))
                 .all())
        if votes:
            for vote in votes:
                db_session.delete(vote)
            db_session.commit()
    except:
        logging.warning("ERROR processing request")
    return ""
