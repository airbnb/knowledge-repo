from ..constants import DOCX
from ..converter import KnowledgePostConverter
from knowledge_repo.utils.files import read_text
import os
import re
import shutil
import tempfile


class DocxConverter(KnowledgePostConverter):

    _registry_keys = [DOCX]

    @property
    def dependencies(self):
        # Dependencies required for this converter on top of core
        # knowledge-repo dependencies
        return ['pypandoc']

    def from_file(self, filename, **opts):
        self.tmp_dir = wd = tempfile.mkdtemp()
        target_file = os.path.join(wd, 'post.md')

        import pypandoc
        pypandoc.convert_file(
            filename,
            format=DOCX,
            to='markdown-grid_tables',
            outputfile=target_file,
            extra_args=[
                '--standalone',
                '--wrap=none',
                f'--extract-media={wd}'
            ]
        )

        md = read_text(target_file)

        # Image embeddings exported from docx files have fixed sizes in inches
        # which browsers do not understand. We remove these annotations.
        md = re.sub(
            r'(\!\[[^\]]+?\]\([^\)]+?\))\{[^\}]+?\}', lambda m: m.group(1), md)

        # Write markdown content to knowledge post (images will be extracted
        # later)
        self.kp_write(md)

    def cleanup(self):
        if hasattr(self, 'tmp_dir'):
            shutil.rmtree(self.tmp_dir)
            del self.tmp_dir
