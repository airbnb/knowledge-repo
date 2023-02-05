""" Define the routes that add/delete comments on posts.

This includes:
  - /comment
  - /comments
  - /delete_comment
"""
from .. import permissions
from ..models import Comment, PageView, Post
from ..proxies import current_user, db_session
from ..utils.emails import send_comment_email
from ..utils.shared import get_blueprint
from flask import escape, request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

blueprint = get_blueprint('comments', __name__)


@blueprint.route('/comment', methods=['POST'])
@PageView.logged
@permissions.post_comment.require()
def post_comment():
    """ Post a comment underneath a post """

    path = request.args.get('path', '')
    comment_id = request.args.get('comment_id')
    data = request.get_json()

    post = (db_session.query(Post)
                      .filter(Post.path == path)
                      .first())

    if not post:
        raise Exception('Unable to find post')

    if comment_id:
        comment = (db_session.query(Comment)
                             .filter(Comment.id == comment_id)
                             .first())
    else:
        comment = Comment(post_id=post.id)
    comment.text = escape(data['text'])
    comment.user_id = current_user.id
    db_session.add(comment)
    db_session.commit()

    send_comment_email(path=path,
                       commenter=current_user.format_name,
                       comment_text=data['text'])
    return "OK"


@post_comment.object_extractor
def post_comment():
    comment_id = request.args.get('comment_id', '')
    return {
        'id': comment_id if comment_id else None,
        'type': 'comment'
    }


@blueprint.route('/delete_comment')
@PageView.logged
@permissions.post_comment.require()
def delete_comment():
    """ Delete a comment """
    try:
        comment_id = int(request.args.get('comment_id', ''))

        comments = (db_session.query(Comment)
                              .filter(Comment.id == comment_id)
                              .all())
        for comment in comments:
            # you can only delete your own comments - silently fail on others
            if comment.user_id == current_user.id:
                db_session.delete(comment)
        db_session.commit()
    except Exception as e:
        logging.warning(f'ERROR processing request: {e}')
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
