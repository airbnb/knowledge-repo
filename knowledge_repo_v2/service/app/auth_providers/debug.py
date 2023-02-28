from ..auth_provider import KnowledgeAuthProvider
from ..models import User
from ..utils.auth import is_safe_url
from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_user
from knowledge_repo.constants import AUTH_LOGIN_FORM, DEBUG, USERNAME
import flask


class DebugAuthProvider(KnowledgeAuthProvider):
    _registry_keys = [DEBUG]

    def prompt(self):
        if request.method == 'POST':
            user = request.form[USERNAME]
            login_user(User(identifier=user))

            flash('Logged in successfully.')

            next = request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            if not is_safe_url(next):
                return flask.abort(400)

            return redirect(next or url_for('index.render_feed'))
        return render_template(AUTH_LOGIN_FORM, skip_password=True)

    def get_user(self):
        return User(identifier=request.form[USERNAME])
