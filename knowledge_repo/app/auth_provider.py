from ..utils.registry import SubclassRegisteringABCMeta
from .utils.auth import prepare_user
from abc import abstractmethod
from flask import (
    current_app,
    redirect,
    session,
    url_for,
    Blueprint,
)
from flask_login import login_user
from flask_principal import identity_changed, Identity
from knowledge_repo.constants import DEBUG, OAUTH


class KnowledgeAuthProvider(object, metaclass=SubclassRegisteringABCMeta):
    _registry_keys = None

    @classmethod
    def register_auth_provider_blueprints(cls, app, prefix='/auth/login'):
        app.auth_providers = []
        for provider in app.config.get('AUTH_PROVIDERS', [DEBUG, OAUTH]):
            if not isinstance(provider, KnowledgeAuthProvider):
                provider = cls._get_subclass_for(
                    provider.lower())(name=provider, app=app)
            app.register_blueprint(
                provider.blueprint,
                url_prefix='/'.join((prefix, provider.name)))
            app.auth_providers.append(provider)

    def __init__(self, name, app=None, **kwargs):
        self.name = name
        self.app = app
        self.blueprint = Blueprint(
            'auth_provider_' + self.name,
            __name__,
            template_folder='../templates'
        )
        self.prepare_blueprint(self.blueprint)
        self.init(**kwargs)

    def init(self):
        pass

    def prepare_blueprint(self, blueprint):
        blueprint.add_url_rule('/', view_func=self.prompt, methods=['GET'])
        blueprint.add_url_rule(
            '/authorize', view_func=self.authorize, methods=['GET', 'POST'])
        return blueprint

    @property
    def link_text(self):
        return f'Sign in using {self.name.capitalize()}'

    @property
    def icon_uri(self):
        return url_for('static', filename=f'images/auth/{self.name}.png')

    def authorize(self):
        user = self.get_user()
        if user is None:
            raise RuntimeError("No such user or invalid credentials")
        assert self.validate(user)
        self._perform_login(user)
        return redirect(session.get('requested_url') or url_for('index.render_feed'))

    def validate(self, user):
        return True

    def _perform_login(self, user):
        user = prepare_user(user)
        login_user(user)

        # Notify flask principal that the identity has changed
        identity_changed.send(current_app._get_current_object(),
                              identity=Identity(user.id))

    @abstractmethod
    def prompt(self):
        pass

    @abstractmethod
    def get_user(self):
        pass
