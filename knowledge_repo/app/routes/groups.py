import logging

from flask import request, render_template, Blueprint
from sqlalchemy import and_

from ..proxies import db_session
from ..models import Group, Post, PageView, User, assoc_group_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


blueprint = Blueprint('groups', __name__,
                      template_folder='../templates', static_folder='../static')


@blueprint.route('/post_groups', methods=['GET'])
@PageView.logged
def groups_for_posts():
    """Given a post_id, return a page where you see a list of groups,
       and can view the group members and add people to groups
    """
    post_id = request.args.get('post_id', 0)
    post = (db_session.query(Post)
                      .filter(Post.id == post_id)
                      .first())
    return render_template('post_groups.html',
                           groups=post.groups)


@blueprint.route('/view_group_users', methods=['GET'])
@PageView.logged
def view_group_users():
    """Given a group_id, return a page with a list of group members"""
    group_id = request.args.get('group_id', 0)
    group = (db_session.query(Group)
                       .filter(Group.id == group_id)
                       .first())
    return render_template('view_group_users.html',
                           group=group)


@blueprint.route('/add_group_users', methods=['GET'])
@PageView.logged
def add_group_users():
    """Given a group_id, show a page where users can be added"""
    group_id = request.args.get('group_id', 0)
    group = (db_session.query(Group)
                       .filter(Group.id == group_id)
                       .first())
    return render_template('add_group_users.html',
                           group=group)


@blueprint.route('/add_users_to_group', methods=['POST', 'GET'])
@PageView.logged
def add_users_to_group():
    group_id = request.args.get('group_id', 0)
    users = request.get_json()
    user_objs = []
    for user in users:
        username = user.strip()
        user_obj = (db_session.query(User)
                              .filter(User.username == username)
                              .first())
        if not user_obj:
            user_obj = User(username=username)
            db_session.add(user_obj)
        user_objs.append(user_obj)

    group_obj = (db_session.query(Group)
                           .filter(Group.id == group_id)
                           .first())
    group_obj.users = user_objs
    db_session.commit()
    return ""


@blueprint.route('/delete_user_from_group', methods=['POST', 'GET'])
@PageView.logged
def delete_user_from_group():
    group_id = request.args.get('group_id', 0)
    user_id = request.get_json()
    user_obj = (db_session.query(User)
                          .filter(User.id == user_id)
                          .first())
    delete_query = (assoc_group_user.delete()
                                    .where(and_(assoc_group_user.c.group_id == group_id,
                                                assoc_group_user.c.user_id == user_obj.id)))
    db_session.execute(delete_query)
    db_session.commit()
    return ""


@blueprint.route('/all_groups', methods=['POST', 'GET'])
@PageView.logged
def all_groups():
    groups = db_session.query(Group).all()
    return render_template('all_groups.html', groups=groups)


@blueprint.route('/add_groups', methods=['POST', 'GET'])
@PageView.logged
def add_groups():
    groups = request.get_json()
    for group_name in groups:
        group = Group(name=group_name)
        db_session.add(group)
    db_session.commit()
    return ""
