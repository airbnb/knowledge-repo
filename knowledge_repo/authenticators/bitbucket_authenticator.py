from ..authenticator import KnowledgeRepositoryAuthenticator
from flask.ext.login import LoginManager, UserMixin

class BitbucketAuthenticator(KnowledgeRepositoryAuthenticator):
    _registry_keys = ['bitbucket']

    def load_user(token):
        raise NotImplementedError


class BitbucketUser(UserMixin):

    def __init__(self, token):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    @property
    def is_active(self):
        raise NotImplementedError

    @property
    def is_authenticated(self):
        raise NotImplementedError

    @property
    def is_anonymous(self):
        raise NotImplementedError

    def get_id(self):
        raise NotImplementedError
