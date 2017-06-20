import sys
from builtins import object
from .utils.registry import SubclassRegisteringABCMeta
from future.utils import with_metaclass
from flask import request, redirect, current_app, session, Blueprint, url_for
from flask_login import LoginManager, login_user


class KnowledgeRepositoryAuthenticator(with_metaclass(SubclassRegisteringABCMeta, object)):
    _registry_keys = None

    def __init__(self, config):
        self._config = config
        self.blueprint.add_url_rule('/', view_func=self.before_login)
        self.blueprint.add_url_rule('/after_authorized', view_func=self.after_authorized)

    def login(self):
        raise NotImplementedError

    @classmethod
    def from_config(cls, config):
        authenticator_name = config.get('USER_AUTHENTICATOR', 'nocheck')
        if authenticator_name.lower() not in cls._registry:
            raise ValueError("The knowledge repository does not recognise user authenticator of name '{}'. Supported authenticators are: {}."
                             .format(authenticator_name, ','.join(list(cls._registry.keys()))))
        return cls._get_subclass_for(authenticator_name)(config)

    @property
    def blueprint(self):
        try:
            self._blueprint
        except AttributeError:
            self._blueprint = Blueprint('auth', __name__)
        return self._blueprint

    def before_login(self):
        return redirect(url_for('auth.after_authorized'))

    def after_authorized(self):
        auth_username_request_header = self._config.get('AUTH_USERNAME_REQUEST_HEADER', 'username_header')
        username = request.headers.get(auth_username_request_header)
        if username:
            login_user(User(username=username))
        if 'original_request_url' in session:
            return redirect(session['original_request_url'])
        else:
            return redirect(url_for('index.render_index'))
