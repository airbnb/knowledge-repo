from ..postprocessor import KnowledgePostProcessor


class StubPostprocessor(KnowledgePostProcessor):
    '''
    Use this to bootstrap your own KnowledgePostProcessor.
    '''
    _registry_keys = None

    def process(self, kp):
        pass
