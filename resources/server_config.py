# This file is only needed for setting up a dedicated server configuration
# with support for extracting username information and emailing users.

# ---------------------------------------------------
# Database configuration
# ---------------------------------------------------
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/knowledge.db'

# Should the database tables be automatically created
DB_AUTO_CREATE = True

# Should the database be automatically migrated when updates exist
# Note: This is True by default if this configuration is not applied,
# under the assumption that if you are concerned about this file
# you are probably interested in minimising risk to stability and handling
# database upgrades manually. Manual database migrations can be
# performed using `knowledge_repo --repo <> db_upgrade ...`.
DB_AUTO_UPGRADE = False


# ---------------------------------------------------
# Repository configuration
# ---------------------------------------------------
# You may specify a function `prepare_repo` which configures
# the repository upon which this server is running. This
# takes place after the repository has been instantiated
# and before the server is able to serve requests. It is
# possible to do anything to the repository, including
# substituting the repository for another one.
# By default, repositories manage their own configurations,
# but this can be risky as they may run arbitrary python code,
# which opens a vector for malicious users to compromise
# the server. If you want to avoid this risk, pass
# the '--safe' (TODO!) option to `knowledge_repo` config and
# manually configure the repository here.
# For example, if your server instance is sitting atop
# a meta-repository, it may make sense to update the meta-repository
# configuration with that of one of its children.
def prepare_repo(repo):
    return repo

# ---------------------------------------------------
# Authentication Headers
# ---------------------------------------------------
# the username request header should allow you to get
# a person's username - this is used for pageview tracking,
# likes, favorites, etc. As a fallback, DEFAULT_USER is used.
AUTH_USERNAME_REQUEST_HEADER = 'username_header'
AUTH_USERNAME_DEFAULT = 'knowledge_default'

# the group request header should allow you to get a
# user's name. This is then used below, where we can
# map specific users to specific projects for the
# webeditor posts
AUTH_GROUP_REQUEST_HEADER = 'user_group_header'
AUTH_GROUP_DEFAULT = ''

USER_GROUP_TO_PROJECT = {}  # TODO: Deprecate?

# ---------------------------------------------------
# Flask Mail Configuration
# Refer to https://pythonhosted.org/flask-mail/
# Unless specified, upstream defaults are used as indicated
# provided that MAIL_SERVER is defined.
# ---------------------------------------------------
# MAIL_SERVER = 'localhost'  # default = 'localhost'
# MAIL_PORT = 25  # default = 25
# MAIL_USE_TLS = False  # default = False
# MAIL_USE_SSL = False  # default = False
# MAIL_DEBUG = False  # default = app.debug
# MAIL_USERNAME = None  # default = None
# MAIL_PASSWORD = None  # default = None
# MAIL_DEFAULT_SENDER = None  # default = None
# MAIL_MAX_EMAILS = None  # default = None
# MAIL_SUPPRESS_SEND = False  # default = app.testing
# MAIL_ASCII_ATTACHMENTS = False  # default = False

# --------------------------------------------------
# Web Editor Configuration
# --------------------------------------------------
# The web editor can be limited to editing posts under
# a limited set of parent directories by setting
# WEB_EDITOR_PREFIXES to a list of supported path prefixes.
# e.g. ['webposts', 'projects']
WEB_EDITOR_PREFIXES = ['webposts']


# ---------------------------------------------------
# Tag configuration
# ---------------------------------------------------
# Posts with certain tags can be excluded from showing up
# in the app. This can be useful for security purposes
EXCLUDED_TAGS = ['private']
