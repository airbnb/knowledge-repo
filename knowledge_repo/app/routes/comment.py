""" Define the routes that add/delete comments on posts.

This includes:
  - /comment
  - /comments
  - /delete_comment
"""
import logging
from flask import request, Blueprint, g

from ..app import db_session
from ..models import Comment, Post, PageView
from ..utils.emails import send_comment_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

blueprint = Blueprint('comments', __name__,
                      template_folder='../templates', static_folder='../static')


@blueprint.route('/comment', methods=['POST'])
@PageView.logged
def post_comment():
    """ Post a comment underneath a post """

    path = request.args.get('path', '')
    comment_id = request.args.get('comment_id', '')
    data = request.get_json()

    post = (db_session.query(Post)
                      .filter(Post.path == path)
                      .first())

    if not post:
        raise Exception('Unable to find post')

    comment = (db_session.query(Comment)
                         .filter(Comment.id == comment_id)
                         .first())
    if not comment:
        comment = Comment(post_id=post.id)

    comment.text = data['text']
    comment.user_id = g.user.id
    db_session.add(comment)
    db_session.commit()

    send_comment_email(post_id=post.id,
                       commenter=g.user.format_name,
                       comment_text=data['text'])
    return ""


@post_comment.object_extractor
def post_comment():
    comment_id = request.args.get('comment_id', '')
    return {
        'id': comment_id if comment_id else None,
        'type': 'comment'
    }


@blueprint.route('/delete_comment')
@PageView.logged
def delete_comment():
    """ Delete a comment """
    try:
        comment_id = int(request.args.get('comment_id', ''))

        comments = (db_session.query(Comment)
                              .filter(Comment.id == comment_id)
                              .all())
        for comment in comments:
            # you can only delete your own comments - silently fail on others
            if comment.user_id == g.user.id:
                db_session.delete(comment)
        db_session.commit()
    except:
        logging.warning("ERROR processing request")
        pass

    return ""


@delete_comment.object_extractor
def delete_comment():
    comment_id = request.args.get('comment_id', '')
    return {
        'id': int(comment_id) if comment_id else None,
        'type': 'comment',
        'action': 'delete'
    }
