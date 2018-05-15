import os
import logging
import subprocess
import tempfile
import frontmatter

from ..converter import KnowledgePostConverter


logger = logging.getLogger(__name__)

# Added to markdown if plotly.js is needed
plotly_header = """<script>
requirejs.config({paths: { 'plotly': ['https://cdn.plot.ly/plotly-latest.min']},});
$(document).on('ready', function(){
    var widget = $(".plotly.html-widget");
    widget.each(function(){
        var div = this,
            json = JSON.parse(this.nextElementSibling.innerHTML),
            data = json.x.data,
            layout = json.x.layout;
        require(["plotly"], function(Plotly) { Plotly.newPlot(div, data, layout);});
    })
});</script>
"""


class RmdConverter(KnowledgePostConverter):
    _registry_keys = ['rmd']

    def from_file(self, filename, rebuild=True):
        Rmd_filename = filename
        if rebuild:
            tmp_fd, tmp_path = tempfile.mkstemp()
            os.close(tmp_fd)

            runcmd = """R --no-save --no-restore --slave -e " \
                        library(rmarkdown); \
                        render('{fname}', '{target_path}', \
                        output_format = html_document(keep_md = T))"
                        """.format(
                            fname = os.path.abspath(filename),
                            target_path = tmp_path
                        )

            # Replace '\' with '\\' on Windows machines so R happy with filepath
            if os.name == 'nt':
                runcmd = runcmd.replace("\\", "\\\\")

            subprocess.check_output(runcmd, shell=True)
            Rmd_filename = tmp_path + ".md"

        post = frontmatter.load(Rmd_filename)
        if "plotly" in post.content:
            post.content = plotly_header + post.content

        self.kp.write(frontmatter.dumps(post))
        self.kp.add_srcfile(filename)

        # Clean up temporary file
        if rebuild:
            os.remove(tmp_path)
