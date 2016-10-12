from __future__ import absolute_import
import os
import imp
import logging
import traceback

from flask import Flask, current_app, render_template, g, request
from flask_mail import Mail
from flask_migrate import Migrate
from alembic import command
from alembic.migration import MigrationContext

from .proxies import db_session, current_repo
from .index import update_index
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
        server_config_defaults = {'SERVER_NAME': 'localhost',
                                  'plugins': []}
        for k, v in server_config_defaults.items():
            self.config[k] = self.config.get(k, v)

        # Register routes to be served
        self.register_blueprint(routes.render.blueprint)
        self.register_blueprint(routes.health.blueprint)
        self.register_blueprint(routes.index.blueprint)
        self.register_blueprint(routes.tags.blueprint)
        self.register_blueprint(routes.vote.blueprint)
        self.register_blueprint(routes.comment.blueprint)
        self.register_blueprint(routes.stats.blueprint)
        self.register_blueprint(routes.web_editor.blueprint)

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
        def update_index_and_typeahead_data():
            """ Function to call all of the steps we want to run recurrently
                Ideally, these functions would be in a background job, but
                running them on each user's first request is a workable
                solution for now.

                Putting these functions in a function wrapper also helps
                because before_first_request decorated functions cannot be
                imported, so this style allows the functions to be used
                across the app in addition to being run at first.
            """

            if not current_app.config.get('REPOSITORY_INDEXING_ENABLED', True):
                return

            typeahead_data = {}

            def update_typeahead_data(post):
                """ Create the typeahead entry for a given knowledge post """
                if post.authors and post.title and post.path:
                    authors_str = [author.format_name for author in post.authors]
                    typeahead_entry = {'author': authors_str,
                                       'title': str(post.title),
                                       'path': str(post.path),
                                       'updated_at': str(post.updated_at)}
                    typeahead_data[str(post.title)] = typeahead_entry

            update_index()

            # For every tag in the excluded tags, create the tag object if it doesn't exist
            # To ensure that posts with the excluded tags do not show up in the typeahead
            excluded_tags = current_app.config.get('EXCLUDED_TAGS', [])
            for tag in excluded_tags:
                tag_exists = (db_session.query(Tag)
                                        .filter(Tag.name == tag)
                                        .all())
                if not tag_exists:
                    tag_exists = Tag(name=tag)
                    db_session.add(tag_exists)
                    db_session.commit()

            posts = (db_session.query(Post)
                     .filter(Post.is_published)
                     .filter(~Post.tags.any(Tag.name.in_(excluded_tags)))
                     .all())

            for post in posts:
                update_typeahead_data(post)

            current_app.config['typeahead_data'] = typeahead_data

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
