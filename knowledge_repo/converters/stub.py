from ..converter import KnowledgePostConverter


class StubConverter(KnowledgePostConverter):
    '''
    Use this as a template for new KnowledgePostConverters.
    '''
    _registry_keys = None

    def from_file(self, filename, **opts):
        raise NotImplementedError

    def from_string(self, filename, **opts):
        raise NotImplementedError

    def to_file(self, filename, **opts):
        raise NotImplementedError

    def to_string(self, **opts):
        raise NotImplementedError
