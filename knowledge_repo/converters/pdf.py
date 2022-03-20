from ..constants import PDF
from ..converter import KnowledgePostConverter
from .html import HTMLConverter
from knowledge_repo.utils.files import write_binary


class PDFConverter(KnowledgePostConverter):
    '''
    Use this as a template for new KnowledgePostConverters.
    '''
    _registry_keys = [PDF]

    @property
    def dependencies(self):
        # Dependencies required for this converter on top of core knowledge-repo dependencies
        return ['weasyprint']

    def from_file(self, filename, **opts):
        raise NotImplementedError

    def from_string(self, filename, **opts):
        raise NotImplementedError

    def to_file(self, filename, **opts):
        write_binary(filename, self.to_string())

    def to_string(self, **opts):
        from weasyprint import HTML, CSS
        html = HTMLConverter(self.kp).to_string()
        return HTML(string=html).write_pdf(stylesheets=[CSS(string='body { font-family: Helvetica, sans-serif !important }')])
