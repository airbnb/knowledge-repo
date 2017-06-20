from ..authenticator import KnowledgeRepositoryAuthenticator
from flask import redirect, url_for, session
from flask_login import LoginManager
from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask_login import login_user

import sys


class BitbucketAuthenticator(KnowledgeRepositoryAuthenticator):
    _registry_keys = ['bitbucket']

    def __init__(self, app):
        oauth_service_config = {
            'base_url': 'https://api.bitbucket.org/2.0/',
            'authorization_url': 'https://bitbucket.org/site/oauth2/authorize',
            'token_url': 'https://bitbucket.org/site/oauth2/access_token',
            'auto_refresh_url': 'https://bitbucket.org/site/oauth2/access_token'
        }
        try:
            oauth_credentials = app.config['OAUTH_CREDENTIALS']['bitbucket']
        except KeyError:
            raise KeyError("credentials for provider 'bitbucket' must be provided under key OAUTH_CREDENTIALS in server_config.py")

        self._blueprint = OAuth2ConsumerBlueprint('auth', __name__,
                                                  login_url='/login',
                                                  authorized_url='/authorized',
                                                  redirect_to='auth.after_authorized',
                                                  **oauth_credentials,
                                                  **oauth_service_config)

        super().__init__(app)

    def before_login(self):
        return redirect(url_for('auth.login'))

    def after_authorized(self):
        bitbucket = self.blueprint.session
        if not bitbucket.authorized:
            return redirect(url_for("auth.before_login"))
        resp = bitbucket.get("user/emails")
        resp_email = resp.json()["values"][0]
        if resp_email["is_primary"] and resp_email["is_confirmed"] and resp_email["type"] == "email":
            pass
            # login_user(User(username=resp_email["email"]))
        print(resp_email["email"], file=sys.stderr)
        return redirect(url_for('index.render_index'))
