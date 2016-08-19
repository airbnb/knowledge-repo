""" Define the routes that add/delete comments on posts.

This includes:
  - /comment
  - /comments
  - /delete_comment
"""
import logging
import json
from flask import request, Blueprint

from ..app import db_session
from ..models import Comment, Post, PageView
from ..utils.emails import send_comment_email
from ..utils.requests import from_request_get_user_info
from ..utils.serialization import to_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

blueprint = Blueprint('comments', __name__,
                      template_folder='../templates', static_folder='../static')


@blueprint.route('/comment', methods=['POST'])
@PageView.log_pageview
def post_comment():
    """ Post a comment underneath a post """

    post_id = request.args.get('post_id', '')
    comment_id = request.args.get('comment_id', '')
    commenter, commenter_id = from_request_get_user_info(request)
    data = request.get_json()

    post = (db_session.query(Post)
            .filter(Post.path == post_id)
            .first())

    comment = (db_session.query(Comment)
               .filter(Comment.id == comment_id)
               .first())
    if not comment:
        comment = Comment(post_id=post.id)

    comment.text = data['text']
    comment.user_id = commenter_id
    db_session.add(comment)
    db_session.commit()

    send_comment_email(post_id=post.id, commenter=commenter,
                       comment_text=data['text'])
    return ""


@blueprint.route('/comments')
@PageView.log_pageview
def get_comments():
    """ Gets all comments for a given post """
    try:
        post_id = request.args.get('post_id', '')
        items = (db_session.query(Comment)
                 .filter(Comment.post_id == post_id)
                 .filter(Comment.type == "post")
                 .all())
        if items:
            return to_json(items)
        else:
            return json.dumps({})
    except:
        logging.warning("ERROR processing request")
        return json.dumps({})


@blueprint.route('/delete_comment')
@PageView.log_pageview
def delete_comment():
    """ Delete a comment """
    try:
        comment_id = int(request.args.get('comment_id', ''))

        items = db_session.query(Comment).filter(
            Comment.id == comment_id).all()
        for item in items:
            db_session.delete(item)
        db_session.commit()
    except:
        logging.warning("ERROR processing request")
        pass

    return ""
