import sys
import re
from builtins import object
from .utils.registry import SubclassRegisteringABCMeta
# from .app.models import User
from future.utils import with_metaclass
from flask import request, redirect, current_app, session, Blueprint, url_for, session
from flask_login import login_user, logout_user, login_required

# decorator for views that do not require login
def login_exempt(f):
    f.login_exempt = True
    return f


class KnowledgeRepositoryAuthenticator(with_metaclass(SubclassRegisteringABCMeta, object)):
    _registry_keys = None

    def __init__(self, app):
        self.app = app
        self.blueprint.add_url_rule('/', view_func=self.before_login)
        self.blueprint.add_url_rule('/after_authorized', view_func=self.after_authorized)
        self.blueprint.add_url_rule('/logout', view_func=self.logout)
        self.blueprint.add_url_rule('/denied', view_func=self.denied)
        self.app.register_blueprint(self.blueprint, url_prefix="/auth")

        # a dummy callable to execute the login_required logic
        login_required_dummy_view = login_required(lambda: None)

        # require login by default
        @app.before_request
        def default_login_required():
            # exclude 404 errors and static routes
            # uses split to handle blueprint static routes as well
            if not request.endpoint or request.endpoint.rsplit('.', 1)[-1] == 'static':
                return

            view = app.view_functions[request.endpoint]

            # bypass auth for any views set to login_exempt
            # bypass auth for this module (otherwise redirect loops will happen)
            if getattr(view, 'login_exempt', False) or re.search('^auth\.', request.endpoint):
                return

            return login_required_dummy_view()

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

    @login_exempt
    def before_login(self):
        auth_username_request_header = self.app.config.get('AUTH_USERNAME_REQUEST_HEADER', 'username_header')
        username = request.headers.get(auth_username_request_header)
        if username:
            user = self.app.login_manager.user_callback(username)
            login_user(user)
        return redirect(url_for('.after_authorized', next=request.args.get('next')))

    @login_exempt
    def after_authorized(self):
        if 'next' in request.args:
            return redirect(request.args.get('next'))
        else:
            return redirect(url_for('index.render_index'))

    def logout(self):
        logout_user()
        return redirect(url_for('index.render_index'))

    def denied(self):
        return "Access Denied"
