import unittest
import uuid
from nose.tools import *
from knowledge_repo import KnowledgeRepository
from flask import current_app, request, redirect, session
from flask_login import login_required, login_user, current_user
from knowledge_repo.app.proxies import login_manager, db_session
from knowledge_repo.app.models import User
from knowledge_repo.authenticators.oauth_authenticator import OAuthAuthenticator
from knowledge_repo.authenticators.nocheck_authenticator import NoCheckAuthenticator


class FlaskLoginUserTest(unittest.TestCase):
    """Test that basic flask-login user model works."""

    def setUp(self):
        self.repo = KnowledgeRepository.for_uri('tests/test_repo', auto_create=True)
        self.repo_app = self.repo.get_app(config='tests/config_server.py')
        # set a random secret_key for test purposes
        self.repo_app.secret_key = str(uuid.uuid4())
        self.app = self.repo_app.test_client()
        self.knowledge_username = 'login_test_user'
        with self.repo_app.app_context():
            @login_manager.unauthorized_handler
            def unauthorized_handler_callback():
                # check is_safe_url before setting this
                session['original_request_url'] = request.url
                return redirect('/login')

            @self.repo_app.route("/tests/login_required_route")
            @login_required
            def login_required_route():
                return ('', 204)

            self.user = User(username=self.knowledge_username)
            if self.user.id is None:
                db_session.commit()
            self.user_id = self.user.id
            username_request_header = self.repo_app.config.get(
                "AUTH_USERNAME_REQUEST_HEADER")
            self.headers = {
                username_request_header: self.knowledge_username
            }

    def test_login_required_unauthorized(self):
        """
        Check that unauthorized user triggers the LoginManager.unauthorized callback
        """
        rv = self.app.get('/tests/login_required_route', headers=self.headers)
        assert (rv.status == "302 FOUND")

    def test_simple_login(self):
        """
        Test a simple endpoint that automatically logs in the user
        """
        with self.repo_app.app_context():
            @self.repo_app.route("/tests/simple_login")
            def simple_login():
                assert_false(current_user.is_authenticated)
                username = request.headers.get(current_app.config.get(
                    'AUTH_USERNAME_REQUEST_HEADER'))
                login_user(User(username=username))
                assert_true(current_user.is_authenticated)
                return ('', 204)

        rv = self.app.get('/tests/simple_login', headers=self.headers)
        assert (rv.status == "204 NO CONTENT")

        rv = self.app.get('/tests/login_required_route', headers=self.headers)
        assert (rv.status == "204 NO CONTENT")

    def test_nocheck_redirect(self):
        """
        Test that the nocheck authenticator automatically logs in the user and redirects to the originally requested URI
        """
        rv = self.app.get('/tests/login_required_route', headers=self.headers)
        assert (rv.status == "302 FOUND")
        assert_true("/login" in rv.headers['Location'])

        with self.repo_app.app_context():
            self.repo_app.authenticator = NoCheckAuthenticator()
        rv = self.app.get('/login', headers=self.headers)
        print(rv.headers)
        assert (rv.status == "302 FOUND")
        assert_true("/tests/login_required_route" in rv.headers['Location'])

        rv = self.app.get('/tests/login_required_route', headers=self.headers)
        assert (rv.status == "204 NO CONTENT")

    def test_oauth_redirect(self):
        """
        Test that the generic OAuth authenticator redirects correctly from the /login endpoint
        """
        with self.repo_app.app_context():
            self.repo_app.config['OAUTH_CREDENTIALS'] = {
                'foo': {
                    'id': 'fooid12345',
                    'secret': 'foosecret12345'
                }
            }
            self.repo_app.config['OAUTH_SERVICES'] = {
                'foo': {
                    'base_url': 'http://localhost/tests/oauth',
                    'request_token_url': None,
                    'access_token_method': 'POST',
                    'access_token_url': 'http://localhost/tests/oauth/access_token',
                    'authorize_url': 'http://localhost/tests/oauth/authorize'
                }
            }
            self.repo_app.authenticator = OAuthAuthenticator('foo')

        rv = self.app.get('/login', headers=self.headers)
        assert_true(False)

if __name__ == '__main__':
    unittest.main()
