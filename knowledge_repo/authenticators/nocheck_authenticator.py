from ..authenticator import KnowledgeRepositoryAuthenticator
from ..app.models import User
from flask import request, redirect, current_app, session
from flask_login import LoginManager, login_user


class NoCheckAuthenticator(KnowledgeRepositoryAuthenticator):
    _registry_keys = ['nocheck']

    def login(self):
        username = request.headers.get(current_app.config.get(
            'AUTH_USERNAME_REQUEST_HEADER'))
        login_user(User(username=username))
        if 'original_request_url' in session:
            return redirect(session['original_request_url'])
        else:
            return redirect('/')
