""" Define the routes that show all the posts.

This includes:
  - /feed
  - /cluster
  - /table
  - /favorites
"""
import os
import json
from builtins import str
from collections import namedtuple
from flask import request, render_template, redirect, Blueprint, current_app, make_response
from flask_login import login_required
from sqlalchemy import case, desc

from .. import permissions
from ..proxies import db_session, current_repo
from ..utils.posts import get_posts
from ..models import Post, Tag, User, PageView
from ..utils.requests import from_request_get_feed_params
from ..utils.render import render_post_tldr

blueprint = Blueprint(
    'index', __name__, template_folder='../templates', static_folder='../static')


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@blueprint.route("/site-map")
@PageView.logged
def site_map():
    links = []
    for rule in current_app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        # if "GET" in rule.methods and has_no_empty_params(rule):
        # url = url_for(rule.endpoint, **(rule.defaults or {}))
        links.append((str(rule), rule.endpoint))
    # links is now a list of url, endpoint tuples
    return u'<br />'.join(str(link) for link in links)


@blueprint.route('/')
@PageView.logged
def render_index():
    return redirect('/feed')


@blueprint.route('/favorites')
@PageView.logged
@login_required
def render_favorites():
    """ Renders the index-feed view for posts that are liked """

    feed_params = from_request_get_feed_params(request)
    user_id = feed_params['user_id']

    user = (db_session.query(User)
            .filter(User.id == user_id)
            .first())
    posts = user.liked_posts

    post_stats = {post.path: {'all_views': post.view_count,
                              'distinct_views': post.view_user_count,
                              'total_likes': post.vote_count,
                              'total_comments': post.comment_count} for post in posts}

    return render_template("index-feed.html",
                           feed_params=feed_params,
                           posts=posts,
                           post_stats=post_stats,
                           top_header='Favorites')


@blueprint.route('/feed')
@PageView.logged
@permissions.index_view.require()
def render_feed():
    """ Renders the index-feed view """
    feed_params = from_request_get_feed_params(request)
    posts, post_stats = get_posts(feed_params)
    for post in posts:
        post.tldr = render_post_tldr(post)

    return render_template("index-feed.html",
                           feed_params=feed_params,
                           posts=posts,
                           post_stats=post_stats,
                           top_header='Knowledge Feed')


@blueprint.route('/table')
@PageView.logged
@permissions.index_view.require()
def render_table():
    """Renders the index-table view"""
    feed_params = from_request_get_feed_params(request)
    posts, post_stats = get_posts(feed_params)
    # TODO reference stats inside the template
    return render_template("index-table.html",
                           posts=posts,
                           post_stats=post_stats,
                           top_header="Knowledge Table",
                           feed_params=feed_params)


@blueprint.route('/cluster')
@PageView.logged
@permissions.index_view.require()
def render_cluster():
    """ Render the cluster view """
    # we don't use the from_request_get_feed_params because some of the
    # defaults are different
    filters = request.args.get('filters', '')
    sort_by = request.args.get('sort_by', 'alpha')
    group_by = request.args.get('group_by', 'folder')
    request_tag = request.args.get('tag')
    sort_desc = not bool(request.args.get('sort_asc', ''))

    excluded_tags = current_app.config.get('EXCLUDED_TAGS', [])
    post_query = (db_session.query(Post)
                            .filter(Post.is_published)
                            .filter(~Post.tags.any(Tag.name.in_(excluded_tags))))

    if filters:
        filter_set = filters.split(" ")
        for elem in filter_set:
            elem_regexp = "%," + elem + ",%"
            post_query = post_query.filter(Post.keywords.like(elem_regexp))

    ClusterPost = namedtuple(
        'ClusterPost',
        ['name', 'is_post', 'children_count', 'content']
    )

    if group_by == "author":
        author_to_posts = {}
        authors = (db_session.query(User).all())
        for author in authors:
            author_posts = [
                ClusterPost(name=post.title, is_post=True,
                            children_count=0, content=post)
                for post in author.posts
                if post.is_published and not post.contains_excluded_tag
            ]
            if author_posts:
                author_to_posts[author.format_name] = author_posts
        grouped_data = [
            ClusterPost(name=k, is_post=False,
                        children_count=len(v), content=v)
            for (k, v) in author_to_posts.items()
        ]

    elif group_by == "tags":
        tags_to_posts = {}
        all_tags = (db_session.query(Tag)
                              .filter(~Tag.name.in_(excluded_tags))
                              .all())

        for tag in all_tags:
            tag_posts = [
                ClusterPost(name=post.title, is_post=True,
                            children_count=0, content=post)
                for post in tag.posts
                if post.is_published and not post.contains_excluded_tag
            ]
            if tag_posts:
                tags_to_posts[tag.name] = tag_posts
        grouped_data = [
            ClusterPost(name=k, is_post=False,
                        children_count=len(v), content=v)
            for (k, v) in tags_to_posts.items()
        ]

    elif group_by == "folder":
        posts = post_query.all()

        # group by folder
        folder_to_posts = {}

        for post in posts:
            folder_hierarchy = post.path.split('/')
            cursor = folder_to_posts

            for folder in folder_hierarchy[:-1]:
                if folder not in cursor:
                    cursor[folder] = {}
                cursor = cursor[folder]

            cursor[folder_hierarchy[-1]] = post

        def unpack(d):
            """
            Recusively unpack folder_to_posts
            """
            children = []
            count = 0
            for k, v in d.items():
                if isinstance(v, dict):
                    l, contents = unpack(v)
                    count += l
                    children.append(
                        ClusterPost(name=k, is_post=False,
                                    children_count=l, content=contents)
                    )
                else:
                    count += 1
                    children.append(
                        ClusterPost(name=k, is_post=True,
                                    children_count=0, content=v)
                    )
            return count, children

        _, grouped_data = unpack(folder_to_posts)

    else:
        raise ValueError(u"Group by `{}` not understood.".format(group_by))

    def rec_sort(content, sort_by):
        sorted_content = []
        for c in content:
            if c.is_post:
                sorted_content.append(c)
            else:
                sorted_content.append(ClusterPost(
                    name=c.name,
                    is_post=c.is_post,
                    children_count=c.children_count,
                    content=rec_sort(c.content, sort_by)
                ))
        # put folders above posts
        clusters = [c for c in sorted_content if not c.is_post]
        posts = [c for c in sorted_content if c.is_post]
        if sort_by == "alpha":
            return (
                sorted(clusters, key=lambda x: x.name) +
                sorted(posts, key=lambda x: x.name)
            )
        else:
            return (
                sorted(clusters, key=lambda x: x.children_count, reverse=sort_desc) +
                sorted(posts, key=lambda x: x.children_count, reverse=sort_desc)
            )

    grouped_data = rec_sort(grouped_data, sort_by)

    return render_template("index-cluster.html",
                           grouped_data=grouped_data,
                           filters=filters,
                           sort_by=sort_by,
                           group_by=group_by,
                           tag=request_tag)


@blueprint.route('/create')
@blueprint.route('/create/<knowledge_format>')
@PageView.logged
@permissions.post_view.require()
def create(knowledge_format=None):
    """ Renders the create knowledge view """
    if knowledge_format is None:
        return render_template("create-knowledge.html",
                               web_editor_enabled=current_app.config['WEB_EDITOR_PREFIXES'] != [])

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    knowledge_template = "knowledge_template.{}".format(knowledge_format)
    filename = os.path.join(cur_dir, '../../templates', knowledge_template)
    response = make_response(open(filename).read())
    response.headers["Content-Disposition"] = "attachment; filename=" + knowledge_template
    return response


@blueprint.route('/ajax/index/typeahead', methods=['GET', 'POST'])
def ajax_post_typeahead():
    if not permissions.index_view.can():
        return '[]'

    # this a string of the search term
    search_terms = request.args.get('search', '')
    search_terms = search_terms.split(" ")
    case_statements = []
    for term in search_terms:
        case_stmt = case([(Post.keywords.ilike('%' + term.strip() + '%'), 1)], else_=0)
        case_statements += [case_stmt]

    match_score = sum(case_statements).label("match_score")

    posts = (db_session.query(Post, match_score)
                       .filter(Post.status == current_repo.PostStatus.PUBLISHED.value)
                       .order_by(desc(match_score))
                       .limit(5)
                       .all())

    matches = []
    for (post, count) in posts:
        authors_str = [author.format_name for author in post.authors]
        typeahead_entry = {'author': authors_str,
                           'title': str(post.title),
                           'path': str(post.path),
                           'keywords': str(post.keywords)}
        matches += [typeahead_entry]
    return json.dumps(matches)


@blueprint.route('/ajax/index/typeahead_tags')
@blueprint.route('/ajax_tags_typeahead', methods=['GET'])
def generate_tags_typeahead():
    if not permissions.index_view.can():
        return '[]'
    return json.dumps([t[0] for t in db_session.query(Tag.name).all()])


@blueprint.route('/ajax/index/typeahead_users')
@blueprint.route('/ajax_users_typeahead', methods=['GET'])
def generate_users_typeahead():
    if not permissions.index_view.can():
        return '[]'
    return json.dumps([u[0] for u in db_session.query(User.identifier).all()])


@blueprint.route('/ajax/index/typeahead_paths')
@blueprint.route('/ajax_paths_typeahead', methods=['GET'])
def generate_projects_typeahead():
    if not permissions.index_view.can():
        return '[]'
    # return path stubs for all repositories
    stubs = [u'/'.join(p.split('/')[:-1]) for p in current_repo.dir()]
    return json.dumps(list(set(stubs)))
