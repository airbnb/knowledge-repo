import json
import logging

from flask import request, url_for, redirect, render_template, current_app, Blueprint, g

from ..proxies import db_session, current_repo
from ..models import User, Post, PageView
from ..utils.render import render_post, render_comment, render_post_raw


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


blueprint = Blueprint('render', __name__,
                      template_folder='../templates', static_folder='../static')


@blueprint.route('/raw', methods=['GET'])
@PageView.logged
def raw():
    """ Show the raw markdown of a post """
    return redirect(url_for('render.render', raw='true', **request.args))


@blueprint.route('/presentation', methods=['GET'])
@PageView.logged
def presentation():
    """ Render the knowledge post as a presentation """
    return redirect(url_for('render.render', presentation='true', **request.args))


@blueprint.route('/render', methods=['GET'])
@PageView.logged
def render():
    """ Render the knowledge post with all the related formatting """

    path = request.args.get('markdown', '')
    raw = request.args.get('raw', False)

    username, user_id = g.user.username, g.user.id

    tmpl = 'markdown-rendered.html'
    if raw:
        tmpl = 'markdown-raw.html'
    elif request.args.get('presentation'):
        # TODO(dan?) fix presentation post
        # presentation_post = {}
        # presentation_post['authors_string'] = post.author_string
        # presentation_post['tldr'] = post.tldr
        # presentation_post['html'] = html
        # html = create_presentation_text(presentation_post)
        tmpl = "markdown-presentation.html"

    if not current_app.config.get('REPOSITORY_INDEXING_ENABLED', True):
        return _render_preview(path=path, tmpl=tmpl)

    post = (db_session.query(Post)
                      .filter(Post.path == path)
                      .first())
    if not post:
        knowledge_aliases = current_repo.config.aliases
        if path in knowledge_aliases:
            # TODO: reframe as redirect
            post = (db_session.query(Post)
                              .filter(Post.path == knowledge_aliases[path])
                              .first())
    if not post:
        raise Exception("unable to find post at {}".format(path))

    if post.contains_excluded_tag:
        # It's possilbe that someone gets a direct link to a post that has an excluded tag
        return render_template("error.html")

    html = render_post(post)
    raw_post = render_post_raw(post) if raw else None

    comments = post.comments
    for comment in comments:
        comment.author = db_session.query(User).filter(User.id == comment.user_id).first().username
        if not raw:
            comment.text = render_comment(comment)

    user_obj = (db_session.query(User)
                          .filter(User.id == user_id)
                          .first())

    tags_list = [str(t.name) for t in post.tags]
    user_subscriptions = [str(s) for s in user_obj.get_subscriptions]

    rendered = render_template(tmpl,
                               html=html,
                               post_id=post.id,
                               post_path=path,
                               raw_post=raw_post,
                               comments=comments,
                               username=username,
                               post_author=post.authors_string,
                               title=post.title,
                               page_views=post.view_count,
                               unique_views=post.view_user_count,
                               likes=post.vote_counted_for_user(user_id=user_id),
                               total_likes=post.vote_count,
                               tags_list=tags_list,
                               user_subscriptions=user_subscriptions,
                               webeditor_buttons=False,
                               web_uri=post.kp.web_uri,
                               table_id=None)
    return rendered


def _render_preview(path, tmpl):
    post = None
    if current_repo.has_post(path):
        post = current_repo.post(path)
    else:
        knowledge_aliases = current_repo.config.aliases
        if path in knowledge_aliases:
            # TODO: reframe as redirect
            post = current_repo.post(knowledge_aliases[path])

    if not post:
        raise Exception("unable to find post at {}".format(path))

    html = render_post(post)
    raw_post = render_post_raw(post) if raw else None

    return render_template(tmpl,
                           html=html,
                           post_id=None,
                           post_path=path,
                           raw_post=raw_post,
                           comments=[],
                           username=None,
                           post_author=', '.join(post.headers['authors']),
                           title=post.headers['title'],
                           page_views=0,
                           unique_views=0,
                           likes=1,
                           total_likes=0,
                           tags_list=','.join(post.headers.get('tags', [])),
                           user_subscriptions=[],
                           webeditor_buttons=False,
                           table_id=None)


@render.object_extractor
def render():
    post_path = request.args.get('markdown', '')
    return {
        'id': Post.query.filter(Post.path == post_path).first().id,
        'type': 'post',
        'action': 'view'
    }


@blueprint.route('/about', methods=['GET'])
@PageView.logged
def about():
    """Renders about page. This is the html version of REAMDE.md"""
    return render_template("about.html")


@blueprint.route('/ajax_post_typeahead', methods=['GET', 'POST'])
def ajax_post_typehead():
    return json.dumps(current_app.config.get('typeahead_data', {}))
