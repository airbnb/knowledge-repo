from .utils.registry import SubclassRegisteringABCMeta


class KnowledgePostProcessor(object, metaclass=SubclassRegisteringABCMeta):
    _registry_keys = []

    def process(self, kp):
        return None
