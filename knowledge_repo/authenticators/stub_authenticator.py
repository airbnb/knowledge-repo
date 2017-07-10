from ..authenticator import KnowledgeRepositoryAuthenticator
from flask_login import LoginManager


class StubAuthenticator(KnowledgeRepositoryAuthenticator):
    '''
    Use this as a template for new KnowledgeRepositoryAuthenticators.
    '''
    _registry_keys = None

    def __init__(self, config):
        super().__init__(config)

    def before_login(self):
        raise NotImplementedError

    def after_authorized(self):
        raise NotImplementedError
