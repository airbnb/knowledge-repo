from __future__ import absolute_import
from __future__ import unicode_literals
import markdown
from markdown import Extension
from markdown.preprocessors import Preprocessor
import re
import base64
import mimetypes

from ..converter import KnowledgePostConverter
from ..mapping import SubstitutionMapper

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
                        'markdown.extensions.wikilinks',
                        'knowledge_repo.converters.html:KnowledgeMetaExtension',
                        'knowledge_repo.converters.html:MathJaxExtension']


class KnowledgeMetaPreprocessor(Preprocessor):
    """ Get Meta-Data. """

    def run(self, lines):
        """ Parse Meta-Data and store in Markdown.Meta. """
        cnt = 0
        for i, line in enumerate(lines):
            if line.strip() == '---':
                cnt = cnt + 1
            if cnt == 2:
                break
        return lines[i + 1:]


class KnowledgeMetaExtension(Extension):
    """ Meta-Data extension for Python-Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add MetaPreprocessor to Markdown instance. """
        md.preprocessors.add("knowledge_meta",
                             KnowledgeMetaPreprocessor(md),
                             ">normalize_whitespace")


class MathJaxPattern(markdown.inlinepatterns.Pattern):

    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(self, r'(?<!\\)(\$\$?)(.+?)\2')

    def handleMatch(self, m):
        node = markdown.util.etree.Element('mathjax')
        node.text = markdown.util.AtomicString(m.group(2) + m.group(3) + m.group(2))
        return node


class MathJaxExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        # Needs to come before escape matching because \ is pretty important in LaTeX
        md.inlinePatterns.add('mathjax', MathJaxPattern(), '<escape')


class HTMLConverter(KnowledgePostConverter):
    '''
    Use this as a template for new KnowledgePostConverters.
    '''
    _registry_keys = ['html']

    def init(self):
        self.kp_images = self.kp.read_images()

    def to_string(self, skip_headers=False, images_base64_encode=True, urlmappers=[]):
        """
        Renders the markdown as html
        """
        # Copy urlmappers locally so we can modify it without affecting global
        # state
        urlmappers = urlmappers[:]
        if images_base64_encode:
            urlmappers.insert(0, self.base64_encode_image_mapper)

        html = ''
        if not skip_headers:
            html += self.render_headers()
        html += markdown.Markdown(extensions=MARKDOWN_EXTENSTIONS).convert(self.kp.read())

        return self.apply_url_remapping(html, urlmappers)

    def apply_url_remapping(self, html, urlmappers):
        patterns = {
            'img': '<img.*?src=[\'"](?P<url>.*?)[\'"].*?>',
            'a': '<a.*?href=[\'"](?P<url>.*?)[\'"].*?>'
        }

        def urlmapper_proxy(name, match):
            for urlmapper in urlmappers:
                new_url = urlmapper(name, match.group('url'))
                if new_url is not None:
                    break
            if new_url is not None:
                return re.sub('(src|href)=[\'"](?:.*?)[\'"]', '\\1="{}"'.format(new_url), match.group(0))
            return None

        return SubstitutionMapper(patterns=patterns, mappers=[urlmapper_proxy]).apply(html)

    # Utility methods
    def render_headers(self):
        headers = self.kp.headers

        headers['authors_string'] = ', '.join(headers.get('authors'))
        headers['tldr'] = markdown.Markdown(extensions=MARKDOWN_EXTENSTIONS[
                                            :-1]).convert(headers['tldr'])
        headers['date_created'] = headers['created_at'].isoformat()
        headers['date_updated'] = headers['updated_at'].isoformat()

        header = """
<h1>{title}</h1>
<p id='metadata'>
<strong>Author</strong>: {authors_string} <br>
<strong>Date Created</strong>: {date_created}<br>
<strong>Date Updated</strong>: {date_updated}<br>
<strong>Tags</strong><text>: </text><br>
<strong>TLDR</strong>: {tldr}<br>
</p>
""".format(**headers)

        return header

    def base64_encode_image_mapper(self, tag, url):
        if tag == 'img':
            if url in self.kp_images:
                image_data = base64.b64encode(self.kp_images[url])
                image_mimetype = mimetypes.guess_type(url)[0]
                if image_mimetype is not None:
                    return 'data:{};base64, '.format(image_mimetype) + image_data.decode('utf-8')
        return None
