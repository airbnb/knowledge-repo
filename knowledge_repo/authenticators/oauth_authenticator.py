from ..authenticator import KnowledgeRepositoryAuthenticator
from ..app.models import User
# import uuid
from flask import current_app, url_for, request, redirect, session
from flask_login import LoginManager, current_user
from flask_dance.consumer import OAuth2ConsumerBlueprint
import sys


class OAuthAuthenticator(KnowledgeRepositoryAuthenticator):
    _registry_keys = None

    def __init__(self, provider_name, oauth_credentials, oauth_service_config):
        self._blueprint = OAuth2ConsumerBlueprint(provider_name, 'app',
                                                 **oauth_credentials,
                                                 **oauth_service_config)

    @property
    def blueprint(self):
        return self._blueprint

    def login(self):
        if not current_user.is_anonymous:
            return redirect(url_for('index.render_index'))
        # session['random_key_' + str(uuid.uuid4())] = 'random_value_' + str(uuid.uuid4())
        # print(session, file=sys.stderr)
        return redirect(url_for("bitbucket.login"))

    def oauth_callback(self):
        if not current_user.is_anonymous:
            return redirect(url_for('/'))
        next_url = request.args.get('next') or url_for('index.render_index')
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

        return (resp['oauth_token'], 200)
