from ..authenticator import KnowledgeRepositoryAuthenticator
from flask import redirect, url_for, session, current_app
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
                                                  **oauth_credentials,
                                                  **oauth_service_config)

        @self._blueprint.route('/gitwebhook', methods=['GET'])
        def gitwebhook():
            app.repository.update()
            return ("OK", 200)

        super().__init__(app)

    def before_login(self):
        url_scheme = current_app.config['PREFERRED_URL_SCHEME'] or 'http'
        redirect_url = url_for('auth.after_authorized', _external=True, _scheme=url_scheme)
        return redirect(url_for('auth.login', next=redirect_url))

    def after_authorized(self):
        bitbucket = self.blueprint.session
        if not bitbucket.authorized:
            return redirect(url_for("auth.before_login"))

        # if repository has a Bitbucket remote, check that we can access it or deny access
        if self.app.repository.git_has_remote:
            git_remote_url_parts = self.app.repository.git_remote.url.split(':')
            if git_remote_url_parts[0] == "git@bitbucket.org":
                resp = bitbucket.get("repositories/" + git_remote_url_parts[1].split('.')[0])
                if resp.status_code != 200:
                    return redirect(url_for("auth.denied"))

        # log the user in
        resp = bitbucket.get("user/emails")
        resp_email = resp.json()["values"][0]
        if resp_email["is_primary"] and resp_email["is_confirmed"] and resp_email["type"] == "email":
            user = self.app.login_manager.user_callback(resp_email["email"])
            login_user(user)

        return redirect(url_for('index.render_index'))
