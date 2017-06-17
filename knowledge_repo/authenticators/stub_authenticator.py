from ..authenticator import KnowledgeRepositoryAuthenticator
from flask_login import LoginManager


class StubAuthenticator(KnowledgeRepositoryAuthenticator):
    '''
    Use this as a template for new KnowledgeRepositoryAuthenticators.
    '''
    _registry_keys = None

    def login(self):
        raise NotImplementedError
