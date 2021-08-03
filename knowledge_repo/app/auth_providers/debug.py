import flask
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_user

from ..models import User
from ..utils.auth import is_safe_url

from ..auth_provider import KnowledgeAuthProvider


class DebugAuthProvider(KnowledgeAuthProvider):
    _registry_keys = ['debug']

    def prompt(self):
        if request.method == 'POST':
            user = request.form['username']
            login_user(User(identifier=user))

            flash('Logged in successfully.')

            next = request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            if not is_safe_url(next):
                return flask.abort(400)

            return redirect(next or url_for('index.render_feed'))
        return render_template('auth-login-form.html', skip_password=True)

    def get_user(self):
        return User(identifier=request.form['username'])
