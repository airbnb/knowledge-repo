import os
import re
import shutil
import tempfile

from ..converter import KnowledgePostConverter


class DocxConverter(KnowledgePostConverter):

    _registry_keys = ['docx']

    @property
    def dependencies(self):
        # Dependencies required for this converter on top of core knowledge-repo dependencies
        return ['pypandoc']

    def from_file(self, filename, **opts):
        wd = tempfile.mkdtemp()
        target_file = os.path.join(wd, 'post.md')
        try:
            import pypandoc

            pypandoc.convert_file(
                filename,
                format='docx',
                to='markdown',
                outputfile=target_file,
                extra_args=[
                    '--standalone',
                    '--wrap=none',
                    '--extract-media={}'.format(wd)
                ]
            )

            with open(target_file) as f:
                md = f.read()

            # Image embeddings exported from docx files have fixed sizes in inches
            # which browsers do not understand. We remove these annotations.
            md = re.sub('(\!\[\]\([^\)]+\))\{[^\}]+\}', lambda m: m.group(1), md)

            # Write markdown content to knowledge post (images will be extracted later)
            self.kp_write(md)
        finally:
            shutil.rmtree(wd)
