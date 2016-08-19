import json
import logging

from flask import request, url_for, redirect, render_template, current_app, Blueprint

from ..app import db_session
from ..models import User, Post, PageView
from ..utils.render import render_post, render_comment, render_post_raw
from ..utils.requests import from_request_get_user_info


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


blueprint = Blueprint('render', __name__,
                      template_folder='../templates', static_folder='../static')


@blueprint.route('/raw', methods=['GET'])
@PageView.log_pageview
def raw():
    """ Show the raw markdown of a post """
    return redirect(url_for('render.render', raw='true', **request.args))


@blueprint.route('/presentation', methods=['GET'])
@PageView.log_pageview
def presentation():
    """ Render the knowledge post as a presentation """
    return redirect(url_for('render.render', presentation='true', **request.args))


@blueprint.route('/render', methods=['GET'])
@PageView.log_pageview
def render():
    """ Render the knowledge post with all the related formatting """

    path = request.args.get('markdown', '')
    raw = request.args.get('raw', False)

    username, user_id = from_request_get_user_info(request)

    post = (db_session.query(Post)
                      .filter(Post.path == path)
                      .first())
    if not post:
        knowledge_aliases = current_app.config['repo'].config.aliases
        if path in knowledge_aliases:
            # TODO: reframe as redirect
            post = (db_session.query(Post)
                              .filter(Post.path == knowledge_aliases[path])
                              .first())
    if not post:
        raise Exception("unable to find post at {}".format(path))

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

    tags_list = [str(t.name) for t in post.tags]
    user_subscriptions = [str(s) for s in user_obj.get_subscriptions]

    rendered = render_template(tmpl,
                               html=html,
                               post_id=path,
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
                               table_id=None)
    return rendered


@blueprint.route('/about', methods=['GET'])
def about():
    """Renders about page. This is the html version of REAMDE.md"""
    return render_template("about.html")


@blueprint.route('/ajax_post_typeahead', methods=['GET', 'POST'])
def ajax_post_typehead():
    return json.dumps(current_app.config['typeahead_data'])
