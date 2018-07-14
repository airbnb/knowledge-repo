from __future__ import absolute_import

import multiprocessing
import time
import atexit
import os
import imp
import logging
import traceback
import math
import multiprocessing
import uuid

from flask import Flask, current_app, render_template, g, request, flash, redirect, url_for, session
from flask_login import LoginManager, user_loaded_from_request
from flask_mail import Mail
from flask_migrate import Migrate
from flask_principal import Principal, identity_loaded, identity_changed, Identity, RoleNeed, UserNeed, AnonymousIdentity, PermissionDenied
from alembic import command
from alembic.migration import MigrationContext
from datetime import datetime
from werkzeug import url_encode

import knowledge_repo
from . import roles, routes
from .auth_provider import KnowledgeAuthProvider
from .proxies import db_session, current_repo, current_user
from .index import update_index, set_up_indexing_timers, time_since_index, time_since_index_check
from .models import db as sqlalchemy_db, Post, User, Tag
from .utils.auth import AnonymousKnowledgeUser, populate_identity_roles, prepare_user


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeFlask(Flask):

    def __init__(self, repo, db_uri=None, debug=None, config=None, **kwargs):
        Flask.__init__(self, __name__,
                       template_folder='templates',
                       static_folder='static')

        # Add unique identifier for this application isinstance
        self.uuid = str(uuid.uuid4())
        if 'KNOWLEDGE_REPO_MASTER_UUID' not in os.environ:
            os.environ['KNOWLEDGE_REPO_MASTER_UUID'] = self.uuid

        # Preload default configuration
        self.config.from_object('knowledge_repo.app.config_defaults')

        # Load configuration from file or provided object
        if config:
            if isinstance(config, str):
                config = imp.load_source('knowledge_server_config', os.path.abspath(config))
            self.config.from_object(config)

        # Add configuration passed in as keyword arguments
        self.config.update(kwargs)

        # Prepare repository, and add it to the app
        if hasattr(config, 'prepare_repo'):
            repo = config.prepare_repo(repo)
        self.repository = repo
        assert isinstance(self.repository, knowledge_repo.KnowledgeRepository), "Invalid repository object provided."

        # Set debug mode from kwargs or else maintain current setting
        if debug is not None:
            self.config['DEBUG'] = debug

        # Set the secret key for this instance (creating one if one does not exist already)
        self.config['SECRET_KEY'] = self.config['SECRET_KEY'] or str(uuid.uuid4())

        # Configure database
        if db_uri:
            self.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        logger.debug(u"Using database: {}".format(self.config['SQLALCHEMY_DATABASE_URI']))

        # Register database schema with flask app
        sqlalchemy_db.init_app(self)

        # Set up database migration information
        # Registers Migrate plugin in self.extensions['migrate']
        Migrate(self, self.db)

        # Try to create the database if it does not already exist
        # Existence is determined by whether there is an existing alembic migration revision
        db_auto_create = self.config.get('DB_AUTO_CREATE', True)
        db_auto_upgrade = self.config.get('DB_AUTO_UPGRADE', True)
        if db_auto_create and self.db_revision is None:
            self.db_init()
        elif db_auto_upgrade:
            self.db_upgrade()

        # Initialise login manager to keep track of user sessions
        LoginManager().init_app(self)
        self.login_manager.login_view = 'auth.login'
        self.login_manager.anonymous_user = AnonymousKnowledgeUser

        @self.login_manager.user_loader
        def load_user(user_id):
            return User(identifier=user_id)

        # Attempt login via http headers
        if self.config.get('AUTH_USE_REQUEST_HEADERS'):
            @self.login_manager.request_loader
            def load_user_from_request(request):
                user_attributes = current_app.config.get('AUTH_MAP_REQUEST_HEADERS')(request.headers)
                if isinstance(user_attributes, dict) and user_attributes.get('identifier', None):
                    user = User(identifier=user_attributes['identifier'])
                    user.can_logout = False
                    for attribute in ['avatar_uri', 'email', 'name']:
                        if user_attributes.get(attribute):
                            setattr(user, attribute, user_attributes[attribute])
                    user = prepare_user(user, session_start=False)
                    return user
        elif self.config.get('AUTH_USER_IDENTIFIER_REQUEST_HEADER'):
            logger.warning("AUTH_USER_IDENTIFIER* configuration keys are deprecated and will be removed in v0.9.0 .")

            @self.login_manager.request_loader
            def load_user_from_request(request):
                identifier = request.headers.get(current_app.config['AUTH_USER_IDENTIFIER_REQUEST_HEADER'])
                if identifier:
                    if current_app.config['AUTH_USER_IDENTIFIER_REQUEST_HEADER_MAPPING']:
                        identifier = current_app.config['AUTH_USER_IDENTIFIER_REQUEST_HEADER_MAPPING'](identifier)
                    user = User(identifier=identifier)
                    user.can_logout = False
                    user = prepare_user(user, session_start=False)
                    return user

        # Intialise access policies
        self.principal = Principal(self)

        # Add AnonymousIdentity fallback so that on_identity_loaded is called for
        # anonymous users too.
        self.principal.identity_loaders.append(lambda: AnonymousIdentity())

        # Synchronise user permissions with data model
        @user_loaded_from_request.connect
        def on_user_loaded_from_request(sender, user):
            self.principal.set_identity(Identity(user.id))

        @identity_loaded.connect_via(self)
        def on_identity_loaded(sender, identity):
            populate_identity_roles(identity, user=current_user)

        @self.errorhandler(PermissionDenied)
        def handle_insufficient_permissions(error):
            session['requested_url'] = request.url
            return render_template('permission_denied.html'), 403

        # Add mail object if configuration is supplied
        if self.config.get('MAIL_SERVER'):
            self.config['mail'] = Mail(self)

        # Register routes to be served
        self.register_blueprint(routes.posts.blueprint)
        self.register_blueprint(routes.health.blueprint)
        self.register_blueprint(routes.index.blueprint)
        self.register_blueprint(routes.tags.blueprint)
        self.register_blueprint(routes.vote.blueprint)
        self.register_blueprint(routes.comment.blueprint)
        self.register_blueprint(routes.stats.blueprint)
        self.register_blueprint(routes.editor.blueprint)
        self.register_blueprint(routes.groups.blueprint)
        self.register_blueprint(routes.auth.blueprint)
        KnowledgeAuthProvider.register_auth_provider_blueprints(self)

        if self.config['DEBUG']:
            self.register_blueprint(routes.debug.blueprint)

        # Register error handler
        @self.errorhandler(500)
        def show_traceback(self):
            """ If LOCAL MODE: show the stack trace on a server error
                otherwise show a nice error template to the users
            """
            if current_app.config.get("DEBUG"):
                return render_template('traceback.html', info=traceback.format_exc()), 500
            else:
                return render_template('error.html')

        @self.before_first_request
        def ensure_excluded_tags_exist():
            # For every tag in the excluded tags, create the tag object if it doesn't exist
            excluded_tags = current_app.config['EXCLUDED_TAGS']
            for tag in excluded_tags:
                Tag(name=tag)
            db_session.commit()

        # Set up indexing timers
        set_up_indexing_timers(self)

        @self.before_request
        def open_repository_session():
            if not request.path.startswith('/static'):
                current_repo.session_begin()

        @self.after_request
        def close_repository_session(response):
            if not request.path.startswith('/static'):
                current_repo.session_end()
            return response

        @self.context_processor
        def webediting_enabled():
            # TODO: Link this more to KnowledgeRepository capability and
            # configuration rather than a specific name.
            return {"webeditor_enabled": 'webposts' in current_repo.uris}

        @self.context_processor
        def inject_version():
            version = knowledge_repo.__version__
            version_revision = None
            if '_' in knowledge_repo.__version__:
                version, version_revision = version.split('_')
            return dict(version=version,
                        version_revision=version_revision,
                        last_index=time_since_index(human_readable=True),
                        last_index_check=time_since_index_check(human_readable=True))

        @self.template_global()
        def modify_query(**new_values):
            args = request.args.copy()

            for key, value in new_values.items():
                args[key] = value

            return u'{}?{}'.format(request.path, url_encode(args))

        @self.template_global()
        def pagination_pages(current_page, page_count, max_pages=5, extremes=True):
            page_min = int(max(1, current_page - math.floor(1.0 * max_pages // 2)))
            page_max = int(min(page_count, current_page + math.floor(1.0 * max_pages / 2)))

            to_acquire = max_pages - (page_max - page_min + 1)

            while to_acquire > 0 and page_min > 1:
                page_min -= 1
                to_acquire -= 1
            while to_acquire > 0 and page_max < page_count:
                page_max += 1
                to_acquire -= 1

            pages = list(range(page_min, page_max + 1))
            if extremes:
                if 1 not in pages:
                    pages[0] = 1
                if page_count not in pages:
                    pages[-1] = page_count
            return pages

        @self.template_filter('format_date')
        def format_date(date):
            """
            This will be a Jinja filter that string formats a datetime object.
            If we can't correctly format, we just return the object.
            :type date: Datetime
            :return: A string of the format of YYYY-MM-DD
            :rtype: String
            """
            try:
                return datetime.strftime(date, '%Y-%m-%d')
            except:
                return date

    @property
    def repository(self):
        return getattr(self, '_repository')

    @repository.setter
    def repository(self, repo):
        self._repository = repo

    @property
    def db(self):
        return sqlalchemy_db

    @property
    def _alembic_config(self):
        if not hasattr(self, 'extensions') or 'migrate' not in self.extensions:
            raise RuntimeError("KnowledgeApp has not yet been configured. Please instantiate it via `get_app_for_repo`.")
        migrations_path = os.path.join(os.path.dirname(__file__), "migrations")
        return self.extensions['migrate'].migrate.get_config(migrations_path)

    def db_init(self):
        with self.app_context():
            # Create all tables
            sqlalchemy_db.create_all()

            # Stamp table as being current
            command.stamp(self._alembic_config, "head")

    @property
    def db_revision(self):
        with self.app_context():
            conn = self.db.engine.connect()

            context = MigrationContext.configure(conn)
            return context.get_current_revision()

    def db_upgrade(self):
        with self.app_context():
            command.upgrade(self._alembic_config, "head")

    def db_downgrade(self, revision):
        with self.app_context():
            command.downgrade(self._alembic_config, revision)

    def db_migrate(self, message, autogenerate=True):
        with self.app_context():
            command.revision(self._alembic_config, message=message, autogenerate=autogenerate)

    def db_update_index(self, check_timeouts=True, force=False, reindex=False):
        with self.app_context():
            update_index(check_timeouts=check_timeouts, force=force, reindex=reindex)

    def check_thread_support(self, check_index=True, check_repositories=True):
        # If index database is an sqlite database, it will lock on any write action, and so breaks on multiple threads
        # Repository uris will break as above (but less often since they are not often written too), but will also
        # end up being a separate repository per thread; breaking consistency of presented content.

        if check_index:
            index_db = self.config['SQLALCHEMY_DATABASE_URI']
            if index_db.startswith('sqlite://'):
                return False

        if check_repositories:
            for uri in self.repository.uris.values():
                if uri.startswith('sqlite://') or ':memory:' in uri:
                    return False

        return True
