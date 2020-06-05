from flask import request, render_template, redirect, url_for
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPSocketOpenError

from ..models import User
from ..auth_provider import KnowledgeAuthProvider


class LdapAuthProvider(KnowledgeAuthProvider):
    _registry_keys = ['ldap']

    def init(self):

        if not self.app.config.get('LDAP_SERVER'):
            raise RuntimeError(
                "Use of LDAP authentication requires specification of the LDAP_SERVER configuration variable.")
        self.server = Server(self.app.config['LDAP_SERVER'], get_info=ALL)

    def prompt(self):
        return render_template('auth-login-form.html', skip_password=False)

    def authorize(self):
        user = self.get_user()
        if user is None:
            raise RuntimeError("No such user or invalid credentials")
        if self.validate(user) is False:
            return render_template("auth-login-form.html",
                                   error_message="Uh-oh, it looks like something in your credentials was wrong...")
        self._perform_login(user)
        return redirect(url_for('index.render_feed'))

    def validate(self, user):
        userdn = self.app.config['LDAP_USERDN_SCHEMA'].format(user_id=user.identifier)
        password = request.form['password']

        conn = Connection(self.server, user=userdn, password=password)
        return conn.bind()

    def get_user(self):
        return User(identifier=request.form['username'])
