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
            tmp_fd, tmp_path = tempfile.mkstemp()
            os.close(tmp_fd)

            runcmd = (
                "Rscript --no-save --no-restore --slave -e \""
                "library(knitr);"
                "setwd('{wd}');"
                "knit('{fname}', '{target_path}', quiet=F)"
                "\""
                .format(
                    wd=os.path.abspath(os.path.dirname(filename)),
                    fname=os.path.abspath(filename),
                    target_path=tmp_path
                )
            )

            # Replace '\' with '\\' on Windows machines so R happy with filepath
            if os.name == 'nt':
                runcmd = runcmd.replace("\\", "\\\\")

            subprocess.check_output(runcmd, shell=True)
            Rmd_filename = tmp_path

        with open(Rmd_filename) as f:
            self.kp.write(f.read())
        self.kp.add_srcfile(filename)

        # Clean up temporary file
        if rebuild:
            os.remove(tmp_path)
