from ..authenticator import KnowledgeRepositoryAuthenticator
from ..app.models import User
from flask import current_app, url_for, request
from flask_login import LoginManager, current_user
from flask_oauthlib.client import OAuth


class OAuthAuthenticator(KnowledgeRepositoryAuthenticator):
    _registry_keys = ['oauth']
    providers = None

    def __init__(self, provider_name):
        oauth = OAuth()
        self.provider_name = provider_name
        self.oauth_credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.oauth_service_config = current_app.config['OAUTH_SERVICES'][provider_name]
        self.oauth_remote_app = oauth.remote_app(provider_name,
                                                 **self.oauth_credentials,
                                                 **self.oauth_service_config)

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name, _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

    def login(self):
        if not current_user.is_anonymous:
            return redirect(url_for('index'))
        return self.oauth_remote_app.authorize(
            callback=url_for('auth.oauth_authorized', next=request.args.get('next') or request.referrer or None))

    def oauth_callback(provider):
        if not current_user.is_anonymous():
            return redirect(url_for('index'))
        next_url = request.args.get('next') or url_for('index')
        resp = self.oauth_remote_app.authorized_response()
        if resp is None:
            flash(u'You denied the request to sign in.')
            return redirect(next_url)

        # change this to log the user in and store their token in sqlalchemy
        # how do we get the user id?
        session['oauth_token_response'] = (
            resp['oauth_token'],
            resp['oauth_token_secret']
        )

        return redirect(next_url)
