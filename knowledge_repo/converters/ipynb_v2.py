import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from ..constants import IPYNBv2
from knowledge_repo.utils.files import write_text
from ..converter import KnowledgePostConverter


class IpynbConverterV2(KnowledgePostConverter):
    _registry_keys = [IPYNBv2]

    def from_file(self, filename, **opts):
        # read source notebook
        with open(filename) as f:
            nb = nbformat.read(f, as_version=4)

        # execute notebook
        ep = ExecutePreprocessor(timeout=-1, kernel_name="python3")
        ep.preprocess(nb)

        # export to html
        html_exporter = HTMLExporter()
        html_exporter.exclude_input = True
        (html_data, resources) = html_exporter.from_notebook_node(nb)

        # write to output file
        output_filename = filename.replace(".ipynb", ".html")
        write_text(output_filename, html_data)
