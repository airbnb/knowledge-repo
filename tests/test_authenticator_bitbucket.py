import unittest
import os
import imp
from nose.tools import *
from knowledge_repo import KnowledgeRepository
from flask import Flask, current_app, request, redirect, session, url_for
from flask_login import LoginManager, login_required, login_user, current_user
from knowledge_repo.app.proxies import login_manager, db_session
from knowledge_repo.app.models import User
from knowledge_repo.authenticator import KnowledgeRepositoryAuthenticator


class FlaskLoginUserTest(unittest.TestCase):
    """Test that basic flask-login user model works."""

    def setUp(self):
        # allow oauth over http for testing
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.app = self.repo.get_app(config='tests/config_server_bitbucket.py')
        self.client = self.app.test_client()

        with self.app.app_context():

            @self.app.route("/tests/login_required_route")
            @login_required
            def login_required_route():
                return ('', 204)

            self.knowledge_username = 'login_test_user'
            self.user = self.app.login_manager.user_callback(self.knowledge_username)
            self.headers = {
                self.app.config.get("AUTH_USERNAME_REQUEST_HEADER"): self.knowledge_username
            }

    def test_bitbucket_redirect(self):
        """
        Test that the Bitbucket authenticator redirects correctly from the /auth endpoint
        """
        with self.app.app_context():

            rv = self.client.get(url_for('auth.before_login'), headers=self.headers)
            assert (rv.status == "302 FOUND")
            assert (rv.headers['Location'] == url_for('auth.login'))

            rv = self.client.get(url_for('auth.login'), headers=self.headers)
            assert (rv.status == "302 FOUND")
            assert ('oauth2/authorize' in rv.headers['Location'])

if __name__ == '__main__':
    unittest.main()
