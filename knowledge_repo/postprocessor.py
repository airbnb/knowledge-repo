from builtins import object
from .utils.registry import SubclassRegisteringABCMeta
from future.utils import with_metaclass


class KnowledgePostProcessor(with_metaclass(SubclassRegisteringABCMeta, object)):
    _registry_keys = []

    @classmethod
    def process(cls, kp):
        return None
