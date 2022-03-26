from ..models import Group, PageView, Post, User
from ..proxies import db_session
from ..utils.shared import get_blueprint
from flask import render_template, request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

blueprint = get_blueprint('groups', __name__)


@blueprint.route('/post_groups', methods=['GET'])
@PageView.logged
def groups_for_post():
    """Given a post_id, return a page where you see a list of groups,
       and can view the group members and add people to groups
    """
    post_id = int(request.args.get('post_id', -1))
    post = Post.query.get(post_id)
    return render_template('post_groups.html',
                           groups=post.groups)


@blueprint.route('/view_group_users', methods=['GET'])
@PageView.logged
def view_group_users():
    """Given a group_id, return a page with a list of group members"""
    group_id = int(request.args.get('group_id', -1))
    group = Group.query.get(group_id)
    return render_template('view_group_users.html',
                           group=group)


@blueprint.route('/add_group_users', methods=['GET'])
@PageView.logged
def add_group_users():
    """Given a group_id, show a page where users can be added"""
    group_id = int(request.args.get('group_id', -1))
    group = Group.query.get(group_id)
    return render_template('add_group_users.html',
                           group=group)


@blueprint.route('/add_users_to_group', methods=['POST', 'GET'])
@PageView.logged
def add_users_to_group():
    group_id = int(request.args.get('group_id', -1))
    users = request.get_json()

    group_obj = Group.query.get(group_id)
    group_obj.users_add([user.strip() for user in users])

    db_session.commit()
    return ""


@blueprint.route('/delete_user_from_group', methods=['POST', 'GET'])
@PageView.logged
def delete_user_from_group():
    group_id = int(request.args.get('group_id', 0))
    user_id = int(request.get_json())

    group_obj = Group.query.get(group_id)
    group_obj.users_remove([User.query.get(user_id)])
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
    db_session.commit()
    return ""
