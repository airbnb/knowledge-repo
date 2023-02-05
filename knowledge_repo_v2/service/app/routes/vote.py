""" Define the routes that enable like/unlike on posts.

This includes:
  - /like
  - /unlike
"""
from ..models import PageView, Vote
from ..proxies import current_user, db_session
from ..utils.shared import get_blueprint
import logging
from flask import request
from flask_login import login_required
from sqlalchemy import and_

blueprint = get_blueprint('vote', __name__)


@blueprint.route('/like')
@PageView.logged
@login_required
def like_post():
    """ Like a post """
    try:
        # This will prevent old code from adding invalid post_ids
        post_id = int(request.args.get('post_id', '-1'))
        if post_id < 0:
            return "No Post Found to like!"
        vote = (db_session.query(Vote)
                .filter(and_(Vote.object_id == post_id,
                             Vote.user_id == current_user.id))
                .first())
        if not vote:
            vote = Vote(user_id=current_user.id, object_id=post_id)
            db_session.add(vote)
            db_session.commit()
    except Exception as e:
        logging.warning(f'ERROR processing request {e}')
    return ""


@blueprint.route('/unlike')
@PageView.logged
@login_required
def unlike_post():
    """ Un-like a post """
    try:
        # This will prevent old code from adding invalid post_ids
        post_id = int(request.args.get('post_id', '-1'))
        if post_id < 0:
            return "No Post Found to Unlike!"
        votes = (db_session.query(Vote)
                 .filter(and_(Vote.object_id == post_id,
                              Vote.user_id == current_user.id))
                 .all())
        if votes:
            for vote in votes:
                db_session.delete(vote)
            db_session.commit()
    except Exception as e:
        logging.warning(f'ERROR processing request {e}')
    return ""
