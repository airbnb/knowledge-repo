import sys
import re
from abc import abstractmethod
from builtins import object

# from .app.models import User
from future.utils import with_metaclass
from flask import request, redirect, current_app, session, Blueprint, url_for, session
from flask_login import login_user, logout_user, login_required

from .models import User
from .proxies import db_session
from ..utils.registry import SubclassRegisteringABCMeta


class KnowledgeAuthProvider(with_metaclass(SubclassRegisteringABCMeta, object)):
    _registry_keys = None

    @classmethod
    def register_auth_provider_blueprints(cls, app, prefix='/auth/login'):
        for provider in app.config.get('AUTH_PROVIDERS', ['debug', 'oauth']):
            if not isinstance(provider, KnowledgeAuthProvider):
                provider = cls._get_subclass_for(provider.lower())(name=provider, app=app)
            app.register_blueprint(provider.blueprint, url_prefix='/'.join((prefix, provider.name)))

    def __init__(self, name, app=None, **kwargs):
        self.name = name
        self.app = app
        self.blueprint = Blueprint('auth_provider.' + self.name, __name__, template_folder='../templates')
        self.prepare_blueprint(self.blueprint)
        self.init(**kwargs)

    def init(self):
        pass

    def prepare_blueprint(self, blueprint):
        blueprint.add_url_rule('/', view_func=self.prompt, methods=['GET'])
        blueprint.add_url_rule('/authorize', view_func=self.authorize, methods=['GET', 'POST'])
        return blueprint

    def authorize(self):
        user = self.get_user()
        if user is None:
            raise RuntimeError("No such user or invalid credentials")
        assert self.validate(user)
        self._perform_login(user)
        return redirect(url_for('index.render_feed'))

    def validate(self, user):
        return True

    def _perform_login(self, user):
        db_session.add(user)
        db_session.commit()
        login_user(user)

    @abstractmethod
    def prompt(self):
        pass

    @abstractmethod
    def get_user(self):
        pass