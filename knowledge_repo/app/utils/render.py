import markdown
import os
from flask import url_for
# TODO replace_knowledge_urls, replace_images

MARKDOWN_EXTENSTIONS = ['markdown.extensions.extra',
                        'markdown.extensions.abbr',
                        'markdown.extensions.attr_list',
                        'markdown.extensions.def_list',
                        'markdown.extensions.fenced_code',
                        'markdown.extensions.footnotes',
                        'markdown.extensions.tables',
                        'markdown.extensions.smart_strong',
                        'markdown.extensions.admonition',
                        'markdown.extensions.codehilite',
                        'markdown.extensions.headerid',
                        'markdown.extensions.meta',
                        'markdown.extensions.sane_lists',
                        'markdown.extensions.smarty',
                        'markdown.extensions.toc(baselevel=3)',
                        'markdown.extensions.wikilinks']


def render_post_tldr(post):
    return markdown.Markdown(extensions=MARKDOWN_EXTENSTIONS).convert(post.tldr)


def render_post_header(post):

    author_hrefs = ', '.join(["<a href='{}'>{}</a>".format(
        url_for('index.render_feed', authors=author.username), author.format_name)
        for author in post.authors])

    header = """
    <h1>{title}</h1>
    <p id='metadata'>
    <strong>Author(s): </strong>{author_hrefs} <br>
    <strong>Date Created</strong>: {date_created}<br>
    <strong>Date Updated</strong>: {date_updated}<br>
    <strong>Tags</strong><text>: </text><br>
    <strong>TLDR</strong>: {tldr}<br>
    </p>
    """.format(title=post.title,
               author_hrefs=author_hrefs,
               date_created=post.created_at.isoformat(),
               date_updated=post.updated_at.isoformat(),
               tldr=render_post_tldr(post))

    return header


def render_post_raw(post):
    return post.text.decode('utf-8')


def render_post(post):
    """
    Renders the markdown as html
    """
    def intra_knowledge_urlmapper(name, url):
        if name == 'a' and url.startswith('knowledge:'):
            return url_for('render.render', markdown=url.split('knowledge:')[1])
        return None

    html = render_post_header(post) + post.kp.to_string('html',
                                                        skip_headers=True,
                                                        urlmappers=[intra_knowledge_urlmapper])
    return html


def render_comment(comment):
    return markdown.Markdown().convert(comment.text)
