import os
import logging
import subprocess
import tempfile

from ..converter import KnowledgePostConverter


logger = logging.getLogger(__name__)


class RmdConverter(KnowledgePostConverter):
    _registry_keys = ['rmd']

    def from_file(self, filename, rebuild=True):
        Rmd_filename = filename
        if rebuild:
            _, tmp_path = tempfile.mkstemp()

            runcmd = """R --vanilla --slave -e "library(knitr); setwd('{0}'); \
                        x = knit('{1}', '{2}', quiet=T)" """.format(os.path.abspath(os.path.dirname(filename)),
                                                                    os.path.abspath(filename),
                                                                    tmp_path)
            subprocess.check_output(runcmd, shell=True)
            Rmd_filename = tmp_path

        with open(Rmd_filename) as f:
            self.kp.write(f.read())
        self.kp.add_srcfile(filename)

        # Clean up temporary file
        if rebuild:
            os.remove(tmp_path)
