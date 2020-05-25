from __future__ import absolute_import
from __future__ import unicode_literals
import markdown
from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.preprocessors import Preprocessor
from markdown.util import AtomicString, etree
from markdown.extensions import codehilite, toc
from markdown.inlinepatterns import Pattern

import re
import base64
import mimetypes

from ..converter import KnowledgePostConverter
from ..mapping import SubstitutionMapper

MARKDOWN_EXTENSIONS = ['extra',
                       'abbr',
                       'attr_list',
                       'def_list',
                       'fenced_code',
                       'footnotes',
                       'tables',
                       'admonition',
                       codehilite.CodeHiliteExtension(guess_lang=False),
                       'meta',
                       'sane_lists',
                       'smarty',
                       toc.TocExtension(baselevel=1),
                       'wikilinks',
                       'knowledge_repo.converters.html:KnowledgeMetaExtension',
                       'knowledge_repo.converters.html:MathJaxExtension',
                       'knowledge_repo.converters.html:IndentsAsCellOutput',
                       'knowledge_repo.converters.html:InlineSpanStyles']


class InlineSpanStyles(Extension):

    SPAN_PATTERN = r'\[([\s\S]*?)\]\{((?:\ ?.[^\,\}]+?)*?)\}'

    class SpanMatchHandler(Pattern):
        def handleMatch(self, m):
            # Extract information from markdown tag
            text = m.group(2)

            ids = [
                id
                for id in m.group(3).split(',')
                if id.startswith('#')
            ]
            id = ids[0] if ids else None

            class_names = [
                class_name[1:] if class_name.startswith('.') else class_name
                for class_name in m.group(3).split(' ')
                if class_name.startswith('.')
            ]

            # Generate HTML element for new span
            el = etree.Element('span')
            el.text = text
            if id:
                el.attrib['id'] = id
            if class_names:
                el.attrib['class'] = " ".join(class_names)
            return el

    def extendMarkdown(self, md, md_globals):
        span_matcher = self.SpanMatchHandler(self.SPAN_PATTERN)
        md.inlinePatterns['inline_span'] = span_matcher


class IndentsAsCellOutputPreprocessor(Preprocessor):
    """
    Ensure all indented blocks are followed by a blank line to allow html
    preprocessors to extract html elements (like scripts) properly.
    """

    def run(self, lines):
        in_block = False
        block_startable = True
        for i, line in enumerate(lines):
            if not line.startswith(' ' * self.markdown.tab_length):
                if in_block:
                    if line != "":
                        lines.insert(i, "")
                    in_block = False
                else:
                    block_startable = True if line == "" else False
            elif block_startable and not in_block:
                in_block = True
        return lines


class IndentsAsCellOutputProcessor(BlockProcessor):
    """ Process code blocks. """

    def test(self, parent, block):
        return block.startswith(' ' * self.tab_length)

    def run(self, parent, blocks):
        sibling = self.lastChild(parent)
        block = blocks.pop(0)

        block, theRest = self.detab(block)
        block = block.rstrip()

        block_is_html = False
        if "<div " in block or "</" in block or "<span " in block:
            block_is_html = True

        if (sibling is not None and sibling.tag == "div"):
            # The previous block was a code block. As blank lines do not start
            # new code blocks, append this block to the previous, adding back
            # linebreaks removed from the split into a list.

            block_is_html = block_is_html and not isinstance(sibling.text, AtomicString)

            block = u'\n'.join([sibling.text, block])
            output = sibling
        else:
            # This is a new codeblock. Create the elements and insert text.
            output = markdown.util.etree.SubElement(parent, 'div', {'class': 'code-output'})

        # If not HTML, add the `pre` class so that we know to render output as raw text
        if not block_is_html and 'pre' not in output.get('class', 'code-output'):
            output.set('class', ' '.join([output.get('class', ''), 'pre']))

        output.text = "{}\n".format(block) if block_is_html else AtomicString("{}\n".format(block))

        if theRest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, theRest)


class IndentsAsCellOutput(Extension):

    def extendMarkdown(self, md, md_globals=None):
        md.preprocessors.add("code_isolation",
                             IndentsAsCellOutputPreprocessor(md),
                             "<html_block")
        md.parser.blockprocessors['code'] = IndentsAsCellOutputProcessor(md.parser)


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

    def extendMarkdown(self, md, md_globals=None):
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
    def extendMarkdown(self, md, md_globals=None):
        # Needs to come before escape matching because \ is pretty important in LaTeX
        md.inlinePatterns.add('mathjax', MathJaxPattern(), '<escape')


class HTMLConverter(KnowledgePostConverter):
    '''
    Use this as a template for new KnowledgePostConverters.
    '''
    _registry_keys = ['html']

    def init(self):
        self.kp_images = self.kp.read_images()

    def _render_markdown(self, skip_headers=False, images_base64_encode=True, urlmappers=[]):
        """
        Returns the `Markdown` instance as well as the rendered html output
        as a tuple: (`Markdown`, str).
        """
        # Copy urlmappers locally so we can modify it without affecting global
        # state
        urlmappers = urlmappers[:]
        if images_base64_encode:
            urlmappers.insert(0, self.base64_encode_image_mapper)

        # proxy posts are assumed to be embeddable links
        if 'proxy' in self.kp.headers:
            return None, '<a href="{0}">Linked Post</a>\n<iframe width=100% height=800 src="{0}"></iframe>'.format(self.kp.headers['proxy'].strip())

        html = ''
        if not skip_headers:
            html += self.render_headers()

        md = markdown.Markdown(extensions=MARKDOWN_EXTENSIONS)
        html += md.convert(self.kp.read())

        html = self.apply_url_remapping(html, urlmappers)

        return md, html

    def to_string(self, skip_headers=False, images_base64_encode=True, urlmappers=[]):
        """
        Renders the markdown as html
        """
        return self._render_markdown(
            skip_headers=skip_headers,
            images_base64_encode=images_base64_encode,
            urlmappers=urlmappers
        )[1]

    def apply_url_remapping(self, html, urlmappers):
        patterns = {
            'img': '<img.*?src=[\'"](?P<url>.*?)[\'"].*?>',
            'a': '<a.*?href=[\'"](?P<url>.*?)[\'"].*?>'
        }

        def urlmapper_proxy(name, match):
            for urlmapper in urlmappers:
                new_url = urlmapper(name, match.group('url'))
                if new_url is not None:
                    return match.group(0).replace(match.group('url'), new_url)
            return None

        return SubstitutionMapper(patterns=patterns, mappers=[urlmapper_proxy]).apply(html)

    # Utility methods
    def render_headers(self):
        headers = self.kp.headers

        headers['authors_string'] = ', '.join(headers.get('authors'))
        headers['tldr'] = markdown.Markdown(extensions=MARKDOWN_EXTENSIONS[
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
