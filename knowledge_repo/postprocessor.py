from .utils.registry import SubclassRegisteringABCMeta


class KnowledgePostProcessor(object):
    __metaclass__ = SubclassRegisteringABCMeta
    _registry_keys = []

    @classmethod
    def process(cls, kp):
        return None
