from __future__ import absolute_import
import os
import imp
import logging
import traceback
import math

from flask import Flask, current_app, render_template, g, request
from flask_mail import Mail
from flask_migrate import Migrate
from alembic import command
from alembic.migration import MigrationContext
from datetime import datetime
from werkzeug import url_encode

import knowledge_repo
from .proxies import db_session, current_repo
from .index import update_index, time_since_index, time_since_index_check, _update_index
from .models import db as sqlalchemy_db, Post, User, Tag
from . import routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeFlask(Flask):

    def __init__(self, repo, db_uri=None, debug=None, config=None, **kwargs):
        Flask.__init__(self, __name__,
                       template_folder='templates',
                       static_folder='static')

        # Load configuration
        if config:
            if isinstance(config, str):
                config = imp.load_source('knowledge_server_config', os.path.abspath(config))
            self.config.from_object(config)
        self.config.update(kwargs)

        if hasattr(config, 'prepare_repo'):
            repo = config.prepare_repo(repo)
        self.repository = repo

        # Lift debug mode from underlying KnowledgeRepository object if not specified
        self.config['DEBUG'] = debug if debug is not None else repo.config.debug

        # Configure database
        db_uri = db_uri or self.config.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///:memory:'
        logger.debug("Using database: {}".format(db_uri))
        self.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        self.config['SQLALCHEMY_ECHO'] = repo.config.debug
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

        # Add mail object if configuration is supplied
        if self.config.get('MAIL_SERVER', None) is not None:
            self.config['mail'] = Mail(self)

        # Set config defaults if not included
        # WEB_EDITOR_PREFIXES: Prefixes of repositories that can be edited via the web editor UI
        # Defaults to no prefixes allowed. If None, all prefixes editable via the UI.
        server_config_defaults = {'SERVER_NAME': 'localhost',
                                  'plugins': [],
                                  'WEB_EDITOR_PREFIXES': []}
        for k, v in server_config_defaults.items():
            self.config[k] = self.config.get(k, v)

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
            excluded_tags = current_app.config.get('EXCLUDED_TAGS', [])
            for tag in excluded_tags:
                Tag(name=tag)
            db_session.commit()

        @self.before_request
        def set_user_information():
            if not request.path.startswith('/static'):
                username = current_app.config.get('AUTH_USERNAME_DEFAULT') or 'knowledge_default'
                if current_app.config.get('AUTH_USERNAME_REQUEST_HEADER') is not None:
                    username = request.headers.get(current_app.config.get(
                        'AUTH_USERNAME_REQUEST_HEADER'), username)
                g.user = User(username=username)
                if g.user.id is None:
                    db_session.commit()

        @self.before_request
        def update_index_if_required():
            update_index()

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

            return '{}?{}'.format(request.path, url_encode(args))

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

    def db_migrate(self, message, autogenerate=True):
        with self.app_context():
            command.revision(self._alembic_config, message=message, autogenerate=autogenerate)

    def db_update_index(self, reindex=True):
        with self.app_context():
            _update_index(current_app, force=True, reindex=reindex)

    @property
    def supports_threads(self):
        # If index database is an sqlite database, it will lock on any write action, and so breaks on multiple threads
        # Repository uris will break as above (but less often since they are not often written too), but will also
        # end up being a separate repository per thread; breaking consistency of presented content.

        index_db = self.config['SQLALCHEMY_DATABASE_URI']
        if index_db.startswith('sqlite://') and ':memory:' not in index_db:
            return False

        for uri in self.repository.uris.values():
            if uri.startswith('sqlite://') or ':memory:' in uri:
                return False

        return True
