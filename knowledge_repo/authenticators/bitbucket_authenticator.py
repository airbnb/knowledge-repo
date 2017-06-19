from .oauth_authenticator import OAuthAuthenticator
from ..app.models import User
from flask_login import LoginManager


class BitbucketAuthenticator(OAuthAuthenticator):
    _registry_keys = ['bitbucket']

    def __init__(self, config=None):
        config = config or current_app.config
        oauth_service_config = {
            'base_url': 'https://api.bitbucket.org/2.0/',
            'authorization_url': 'https://bitbucket.org/site/oauth2/authorize',
            'token_url': 'https://bitbucket.org/site/oauth2/access_token',
            'auto_refresh_url': 'https://bitbucket.org/site/oauth2/access_token'
        }
        super().__init__(provider_name='bitbucket',
            oauth_credentials = config['OAUTH_CREDENTIALS']['bitbucket'],
            oauth_service_config = oauth_service_config)
