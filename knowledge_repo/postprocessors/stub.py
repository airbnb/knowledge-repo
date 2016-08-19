from ..postprocessor import KnowledgePostProcessor


class StubPostprocessor(KnowledgePostProcessor):
    '''
    Use this to bootstrap your own KnowledgePostProcessor.
    '''
    _registry_keys = None

    @classmethod
    def process(cls, kp):
        pass
