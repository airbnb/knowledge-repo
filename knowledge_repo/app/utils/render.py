import markdown
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
                        'markdown.extensions.toc(baselevel=3)',
                        'markdown.extensions.wikilinks']


def render_post_tldr(post):
    if isinstance(post, KnowledgePost):
        return markdown.Markdown(extensions=MARKDOWN_EXTENSTIONS).convert(post.headers.get('tldr'))
    else:
        return markdown.Markdown(extensions=MARKDOWN_EXTENSTIONS).convert(post.tldr)


def render_post_header(post):

    header_template = """
    <h1>{title}</h1>
    <p id='metadata'>
    <strong>Author(s): </strong>{author_hrefs} <br>
    <strong>Date Created</strong>: {date_created}<br>
    <strong>Date Updated</strong>: {date_updated}<br>
    <strong>Tags</strong><text>: </text><br>
    <strong>TLDR</strong>: {tldr}<br>
    </p>
    """

    if isinstance(post, KnowledgePost):
        return header_template.format(title=post.headers['title'],
                                      author_hrefs=', '.join(post.headers['authors']),
                                      date_created=post.headers['created_at'].isoformat(),
                                      date_updated=post.headers['updated_at'].isoformat(),
                                      tldr=render_post_tldr(post))
    else:
        author_hrefs = ', '.join(["<a href='{}'>{}</a>".format(
            url_for('index.render_feed', authors=author.username), author.format_name)
            for author in post.authors])
        return header_template.format(title=post.title,
                                      author_hrefs=author_hrefs,
                                      date_created=post.created_at.isoformat(),
                                      date_updated=post.updated_at.isoformat(),
                                      tldr=render_post_tldr(post))


def render_post_raw(post):
    if isinstance(post, KnowledgePost):
        return post.read().encode('ascii', 'ignore')
    else:
        return post.text.encode('ascii', 'ignore')


def render_post(post):
    """
    Renders the markdown as html
    """
    def intra_knowledge_urlmapper(name, url):
        if name == 'a' and url.startswith('knowledge:'):
            return url_for('render.render', markdown=url.split('knowledge:')[1])
        return None

    html = render_post_header(post) + (post if isinstance(post, KnowledgePost) else post.kp).to_string('html',
                                                                                                       skip_headers=True,
                                                                                                       urlmappers=[intra_knowledge_urlmapper])
    return html


def render_comment(comment):
    return markdown.Markdown().convert(comment.text)
