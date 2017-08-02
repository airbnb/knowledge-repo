import sys

import markdown
import pygments
from flask import url_for
from knowledge_repo.post import KnowledgePost

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
                        'markdown.extensions.toc(baselevel=1)',
                        'markdown.extensions.wikilinks',
                        'markdown.extensions.nl2br']


def render_post_tldr(post):
    if isinstance(post, KnowledgePost):
        return markdown.Markdown(extensions=MARKDOWN_EXTENSTIONS).convert(post.headers.get('tldr').strip())
    else:
        return markdown.Markdown(extensions=MARKDOWN_EXTENSTIONS).convert(post.tldr.strip())


def render_post_header(post):

    header_template = u"""
    <div class='metadata'>
    <h1>{title}</h1>
    <span class='authors'>{authors}</span>
    <span class='date_created'>{date_created}</span>
    <span class='date_updated'>(Last Updated: {date_updated})</span>
    <span class='tldr'>{tldr}</span>
    <span class='tags'></span>
    </div>
    """

    def get_authors(usernames, authors):
        authors = [u"<a href='{}'>{}</a>".format(url_for('index.render_feed', authors=username), author) for username, author in zip(usernames, authors)]
        return u' and '.join(u', '.join(authors).rsplit(', ', 1))

    if isinstance(post, KnowledgePost):
        return header_template.format(title=post.headers['title'],
                                      authors=get_authors(post.headers['authors'], post.headers['authors']),
                                      date_created=post.headers['created_at'].strftime("%B %d, %Y"),
                                      date_updated=post.headers['updated_at'].strftime("%B %d, %Y"),
                                      tldr=render_post_tldr(post))
    else:
        return header_template.format(title=post.title,
                                      authors=get_authors([author.identifier for author in post.authors], [author.format_name for author in post.authors]),
                                      date_created=post.created_at.strftime("%B %d, %Y"),
                                      date_updated=post.updated_at.strftime("%B %d, %Y"),
                                      tldr=render_post_tldr(post))


def render_post_raw(post):
    if isinstance(post, KnowledgePost):
        raw_post = post.read().encode('ascii', 'ignore')
    else:
        raw_post = post.text.encode('ascii', 'ignore')

    raw_post = pygments.highlight(
        code=raw_post,
        lexer=pygments.lexers.get_lexer_by_name('md'),
        formatter=pygments.formatters.get_formatter_by_name('html')
    )

    return raw_post


def render_post(post, with_toc=False):
    """
    Renders the markdown as html
    """
    from knowledge_repo.converters.html import HTMLConverter

    def intra_knowledge_urlmapper(name, url):
        if name == 'a' and url.startswith('knowledge:'):
            return url_for('posts.render', path=url.split('knowledge:')[1]).replace('%2F', '/')  # Temporary fix before url revamp
        return None

    md, html = HTMLConverter(post if isinstance(post, KnowledgePost) else post.kp)._render_markdown(skip_headers=True, urlmappers=[intra_knowledge_urlmapper])

    html = render_post_header(post) + html

    if with_toc:
        return {
            "html": html,
            "toc": md.toc if md is not None else None
        }
    return html


def render_comment(comment):
    return markdown.Markdown().convert(comment.text)
