import sys
from builtins import object
from .utils.registry import SubclassRegisteringABCMeta
# from .app.models import User
from future.utils import with_metaclass
from flask import request, redirect, current_app, session, Blueprint, url_for, session
from flask_login import login_user


class KnowledgeRepositoryAuthenticator(with_metaclass(SubclassRegisteringABCMeta, object)):
    _registry_keys = None

    def __init__(self, app):
        self.app = app
        self.blueprint.add_url_rule('/', view_func=self.before_login)
        self.blueprint.add_url_rule('/after_authorized', view_func=self.after_authorized)
        self.app.register_blueprint(self.blueprint, url_prefix="/auth")

    def login(self):
        raise NotImplementedError

    @classmethod
    def from_app(cls, app):
        return cls.subclass_from_config(app.config)(app)

    @classmethod
    def subclass_from_config(cls, config):
        authenticator_name = config.get('USER_AUTHENTICATOR', 'nocheck')
        if authenticator_name.lower() not in cls._registry:
            raise ValueError("The knowledge repository does not recognise user authenticator of name '{}'. Supported authenticators are: {}."
                             .format(authenticator_name, ','.join(list(cls._registry.keys()))))
        return cls._get_subclass_for(authenticator_name)

    @property
    def blueprint(self):
        try:
            self._blueprint
        except AttributeError:
            self._blueprint = Blueprint('auth', __name__)
        return self._blueprint

    def before_login(self):
        auth_username_request_header = self.app.config.get('AUTH_USERNAME_REQUEST_HEADER', 'username_header')
        username = request.headers.get(auth_username_request_header)
        if username:
            user = self.app.login_manager.user_callback(username)
            login_user(user)
        return redirect(url_for('auth.after_authorized', next=request.args.get('next')))

    def after_authorized(self):
        if 'next' in request.args:
            return redirect(request.args.get('next'))
        else:
            return redirect(url_for('index.render_index'))
