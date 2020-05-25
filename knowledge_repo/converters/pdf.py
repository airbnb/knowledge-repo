from ..converter import KnowledgePostConverter

from .html import HTMLConverter


class PDFConverter(KnowledgePostConverter):
    '''
    Use this as a template for new KnowledgePostConverters.
    '''
    _registry_keys = ['pdf']

    @property
    def dependencies(self):
        # Dependencies required for this converter on top of core knowledge-repo dependencies
        return ['weasyprint']

    def from_file(self, filename, **opts):
        raise NotImplementedError

    def from_string(self, filename, **opts):
        raise NotImplementedError

    def to_file(self, filename, **opts):
        with open(filename, 'wb') as f:
            f.write(self.to_string())

    def to_string(self, **opts):
        from weasyprint import HTML, CSS
        html = HTMLConverter(self.kp).to_string()
        return HTML(string=html).write_pdf(stylesheets=[CSS(string='body { font-family: Helvetica, sans-serif !important }')])
