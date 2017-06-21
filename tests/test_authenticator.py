import unittest
import os
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
        self.app = self.repo.get_app(config='tests/config_server_nocheck.py')
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

    def test_login_required_unauthorized(self):
        """
        Check that unauthorized user triggers the LoginManager.unauthorized callback
        """
        rv = self.client.get('/tests/login_required_route', headers=self.headers)
        assert (rv.status == "302 FOUND")

    def test_simple_login(self):
        """
        Test a simple endpoint that automatically logs in the user
        """
        with self.app.app_context():
            @self.app.route("/tests/simple_login")
            def simple_login():
                assert_false(current_user.is_authenticated)
                username = request.headers.get(current_app.config.get(
                    'AUTH_USERNAME_REQUEST_HEADER'))
                login_user(User(username=username))
                assert_true(current_user.is_authenticated)
                return ('', 204)

        rv = self.client.get('/tests/simple_login', headers=self.headers)
        assert (rv.status == "204 NO CONTENT")

        rv = self.client.get('/tests/login_required_route', headers=self.headers)
        assert (rv.status == "204 NO CONTENT")

    def test_nocheck_login(self):
        """
        Test that the nocheck authenticator automatically logs in the user and redirects to the originally requested URI
        """
        with self.app.app_context():
            rv = self.client.get('/tests/login_required_route', headers=self.headers)
            assert (rv.status == "302 FOUND")
            print(rv.headers['Location'])
            assert (url_for('auth.before_login') in rv.headers['Location'])

            rv = self.client.get(rv.headers['Location'], headers=self.headers)
            assert (rv.status == "302 FOUND")
            assert (url_for('auth.after_authorized') in rv.headers['Location'])

            rv = self.client.get(rv.headers['Location'], headers=self.headers)
            assert (rv.status == "302 FOUND")
            assert ('/tests/login_required_route' in rv.headers['Location'])

            rv = self.client.get('/tests/login_required_route', headers=self.headers)
            assert (rv.status == "204 NO CONTENT")

    def test_nocheck_logout(self):
        """
        Test that the nocheck authenticator logs out an authenticated user when requested
        """
        with self.app.app_context():
            rv = self.client.get(url_for('auth.before_login'), headers=self.headers)
            assert (rv.status == "302 FOUND")

            rv = self.client.get(rv.headers['Location'], headers=self.headers)
            assert (rv.status == "302 FOUND")

            rv = self.client.get('/tests/login_required_route', headers=self.headers)
            assert (rv.status == "204 NO CONTENT")

            rv = self.client.get(url_for('auth.logout'), headers=self.headers)
            assert (rv.status == "302 FOUND")

            rv = self.client.get('/tests/login_required_route', headers=self.headers)
            assert (rv.status == "302 FOUND")

    @raises(ValueError)
    def test_unknown_named_authenticator(self):
        """
        Test that instantiating a nonexistent named authenticator raises a ValueError
        """
        fooAuthenticator = KnowledgeRepositoryAuthenticator.subclass_from_config({
            'USER_AUTHENTICATOR': 'foo'
        })

if __name__ == '__main__':
    unittest.main()
