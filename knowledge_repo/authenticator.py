
from builtins import object
from .utils.registry import SubclassRegisteringABCMeta
from future.utils import with_metaclass


class KnowledgeRepositoryAuthenticator(with_metaclass(SubclassRegisteringABCMeta, object)):
    _registry_keys = None

    def login(self):
        raise NotImplementedError

    @classmethod
    def by_name(cls, authenticator_name):
        if authenticator_name.lower() not in cls._registry:
            raise ValueError("The knowledge repository does not recognise user authenticator of name '{}'. Supported authenticators are: {}."
                             .format(authenticator_name, ','.join(list(cls._registry.keys()))))
        return cls._get_subclass_for(authenticator_name)
