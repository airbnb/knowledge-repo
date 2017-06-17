from .bitbucket_authenticator import OAuthAuthenticator
from ..app.models import User
from flask_login import LoginManager


class BitbucketAuthenticator(OAuthAuthenticator):
    _registry_keys = ['bitbucket']

    def login(self):
        raise NotImplementedError
