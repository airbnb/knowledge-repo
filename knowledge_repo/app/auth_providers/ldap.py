
from flask import request, render_template
from ldap3 import Server, Connection, ALL

from ..models import User
from ..auth_provider import KnowledgeAuthProvider


class LdapAuthProvider(KnowledgeAuthProvider):
    _registry_keys = ['ldap']

    def init(self):
        # Create server connection
        address = "ldap://127.0.0.1:389" # Move to Config file
        self.server = Server(address, get_info=ALL)

    def prompt(self):
        return render_template('auth-login-form.html', skip_password=False)

    def validate(self, user):
        user_id = user.identifier
        password = request.form['password']
        userdn_string = "cn={0},ou=people,dc=planetexpress,dc=com"  # Move to Config file
        conn = Connection(self.server, user=userdn_string.format(user_id), password=password)
        return conn.bind()

    # TODO: Populate user with LDAP INFO. Put LDAP Schema in config file?
    def get_user(self):
        return User(identifier=request.form['username'])