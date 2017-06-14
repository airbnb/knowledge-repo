
from builtins import object
from .utils.registry import SubclassRegisteringABCMeta
from future.utils import with_metaclass

class KnowledgeRepositoryAuthenticator(with_metaclass(SubclassRegisteringABCMeta, object)):
    _registry_keys = None

    def load_user(token):
        raise NotImplementedError
