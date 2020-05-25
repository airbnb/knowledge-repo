from builtins import object
from .utils.registry import SubclassRegisteringABCMeta
from future.utils import with_metaclass


class KnowledgePostProcessor(with_metaclass(SubclassRegisteringABCMeta, object)):
    _registry_keys = []

    def process(self, kp):
        return None
