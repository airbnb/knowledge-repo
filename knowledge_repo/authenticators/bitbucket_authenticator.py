import flask

# At the moment flask-dance will return an HTTP /authorized callback if the original request is HTTP
# This can cause an insecure transport error when running the app behind a load balancer etc.
# We need to monkey patch url_for to allow us to force external URLs to be HTTPS

original_url_for = flask.url_for


def monkey_patch_url_for(endpoint, **values):
    if 'OAUTH_FORCE_HTTPS' in flask.current_app.config and '_external' in values:
        if flask.current_app.config['OAUTH_FORCE_HTTPS'] and values['_external']:
            values['_scheme'] = 'https'
    return original_url_for(endpoint, **values)

flask.__dict__['url_for'] = monkey_patch_url_for

from ..authenticator import KnowledgeRepositoryAuthenticator
from flask import redirect, url_for, session, current_app
from flask_login import LoginManager, login_user
from flask_dance.consumer import OAuth2ConsumerBlueprint


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

        @self._blueprint.route('/gitwebhook', methods=['GET'])
        def gitwebhook():
            app.repository.update()
            return ("OK", 200)

        super().__init__(app)

    def before_login(self):
        return redirect(url_for('auth.login'))

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
