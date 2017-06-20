from ..authenticator import KnowledgeRepositoryAuthenticator
from ..app.models import User
from flask import request, redirect, current_app, session
from flask_login import LoginManager, login_user


class NoCheckAuthenticator(KnowledgeRepositoryAuthenticator):
    _registry_keys = ['nocheck']

    def __init__(self, config):
        super().__init__(config)
