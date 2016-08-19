

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown import Extension
from markdown.preprocessors import Preprocessor


class KnowledgeMetaExtension(Extension):
    """ Meta-Data extension for Python-Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add MetaPreprocessor to Markdown instance. """
        md.preprocessors.add("knowledge_meta",
                             KnowledgeMetaPreprocessor(md),
                             ">normalize_whitespace")


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


def makeExtension(*args, **kwargs):
    return KnowledgeMetaExtension(*args, **kwargs)
