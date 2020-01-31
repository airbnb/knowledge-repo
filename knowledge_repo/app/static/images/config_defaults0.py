import datetime
# ---------------------------------------------------
# Host configuration
# ---------------------------------------------------

# The server name is used by Flask to limit access to the
# served content to request to a particular domain. It
# is also used by some authentication providers (in particular
# OAuth providers) to advertise callback providers. If
# not provided, it is assumed in these contexts to be
# 'localhost:7000'. Be sure to specify this before deploying
# into production.
SERVER_NAME = None

# The knowledge repository uses the secret key to sign user
# sessions. If not specified, a unique secret key will be
# generated every time the server starts up. If hosting
# in a multi-server environment, or you want sessions
# to persist accross server restarts, set this to something
# static.
SECRET_KEY = None

# Set DEPLOY_HTTPS to True if you want to enable encrypted
# communication with Flask. When enabled, you must provide
# your ssl certificate, which consists of a .crt and .key
# file.
# Note: Even if you set DEPLOY_HTTPS to True, you still need
# to set the port to 443 manually.
DEPLOY_HTTPS = False
SSL_CERT = {
    'cert': '/path/to/cert',
    'key': '/path/to/key'
}

# ---------------------------------------------------
# Debug configuration
# ---------------------------------------------------
DEBUG = False

# ---------------------------------------------------
# Database configuration
# ---------------------------------------------------
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

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
# Authentication configuration
# ---------------------------------------------------
# Authentication providers allow users to sign into the Knowledge Repo
# in a variety of different ways. You can create your own subclass of
# `KnowledgeAuthProvider` and add either the instance or identifier
# used for that class below.
# By default, the knowledge repo offers:
# ['debug', 'oauth2', 'bitbucket', 'github', 'google']
AUTH_PROVIDERS = []

# If you are going to use a OAuth provider, you will need to specify client ids
# and private tokens. This can be done by instantiating instances of
# `OAuth2Provider` and adding them to the above list, or by specifying OAuth
# connection properties as demonstrated below for the GitHub authenticator.
# OAUTH_GITHUB_CLIENT_ID = '<client id>'
# OAUTH_GITHUB_CLIENT_SECRET = '<client secret>'

# To configure a generic OAuth provider that is not one of the presets
# provided, you may use the provider 'oauth2' which creates an empty,
# unconfigured OAuth2Provider. You must then override its configuration.
# For example, for a self-managed Gitlab CE instance at gitlab.example.com:

# OAUTH_OAUTH2_BASE_URL = 'https://gitlab.example.com/api/v4/'
# OAUTH_OAUTH2_AUTHORIZATION_URL = 'https://gitlab.example.com/oauth/authorize'
# OAUTH_OAUTH2_TOKEN_URL = 'https://gitlab.example.com/oauth/token'
# OAUTH_OAUTH2_AUTO_REFRESH_URL = 'https://gitlab.example.com/oauth/token'
# OAUTH_OAUTH2_SCOPES = 'api'
# OAUTH_OAUTH2_USER_INFO_ENDPOINT = 'user'
# OAUTH_OAUTH2_USER_INFO_MAPPING = {
#     'identifier': 'username',
#     'name': 'name',
#     'avatar_uri': 'avatar_url'
# }
# OAUTH_OAUTH2_VERIFY_SSL_CERTS = '/path/to/certs/my.ca-bundle'
# OAUTH_OAUTH2_CLIENT_ID = '<client id>'
# OAUTH_OAUTH2_CLIENT_SECRET = '<client secret>'

# The configuration OAUTH_<name>_VERIFY_SSL_CERTS is what is passed to the
# 'verify' parameter in the Requests module, and can be used to disable
# HTTPS verification (not recommended) or provide a custom CA bundle. See:
# http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification

# You may also override the .validate() method of a KnowledgeAuthProvider
# to perform an additional validation step before authenticating a user.
# The following example checks whether a user has access to the git remote
# of the local Knowledge Repository:

# def OAUTH_OAUTH2_VALIDATE(provider, user):
#
#     if provider.app.repository.git_has_remote:
#
#         url_parts = (
#             provider.app.repository.git_remote.url.split(':')
#             )
#
#         url_subparts = url_parts[1].split('/')
#
#         if url_parts[0] == "git@gitlab.example.com":
#             git_project = (
#                 url_subparts[0] + "%2F" + url_subparts[1].split('.')[0])
#         elif (
#             url_parts[0] == "https"
#             and url_subparts[2] == "gitlab.example.com"
#         ):
#             git_project = (
#                 url_subparts[3] + "%2F" + url_subparts[4].split('.')[0])
#         else:
#             provider.app.logger.warning(
#                 "User validation failed: unexpected git remote url ["
#                 + provider.app.repository.git_remote.url + "]")
#             return False
#
#         user_validate_url = provider.base_url + "projects/" + git_project
#
#         resp = provider.oauth_client.get(
#             user_validate_url,
#             verify=OAUTH_OAUTH2_VERIFY_HTTPS)
#
#         if resp.status_code == 200:
#             return True
#         else:
#             provider.app.logger.warning(
#                 "User validation failed: validation URL ["
#                 + user_validate_url + "] returned HTTP status ["
#                 + str(resp.status_code) + "]")

# You can also forgo a fully-fledged sign in process for users by hosting the
# knowledge repository behind a proxy server that pre-authenticates users, and
# adds the appropriate user identifier to the http headers of the request. If
# enabled below, then they take precedence over any other forms of
# authentication. If the call to `AUTH_MAP_REQUEST_HEADERS` results in a null
# user identifier, then the authentication flow will fall back to use any of the
# providers specified above.
AUTH_USE_REQUEST_HEADERS = False


# If using headers to authenticate, the following function should be implemented
# to transform a dictionary of headers into a dictionary of user attributes.
# Currently only 'identifier', 'avatar_uri', 'name' and 'email' are supported.
# If this method returns `None`, or `identifier` is not supplied, then the
# authorization flow will fall back to other authentication methods.
def AUTH_MAP_REQUEST_HEADERS(headers):
    return {
        # 'identifier': None,
        # 'avatar_uri': None,
        # 'name': None,
        # 'email': None
    }


# The following AUTH_USER_IDENTIFIER* configuration keys are deprecated and
# will be removed in v0.9.
AUTH_USER_IDENTIFIER_REQUEST_HEADER = None


def AUTH_USER_IDENTIFIER_REQUEST_HEADER_MAPPING(identifier):
    return identifier


# If the server desires to modify the attributes of the `User` object associated with
# users logged in via any of the above authentication providers, it can do so via
# this configuration key. This function will be run once at user login (if using
# an `AuthenticationProvider`, and then at most once during any caching lifetime
# period (as specified below). Note that attributes collected via
# `AuthenticationProvider`s will not be updated after initial login (user must
# relogin in order to reset those attributes).
def AUTH_USER_ATTRIBUTE_SETTER(user):
    return user


# The time to wait before re-checking user attributes with the above function
# for users logged in via request headers.
AUTH_USER_ATTRIBUTE_CACHE_LIFETIME = 24 * 60 * 60  # 1 day

# Once a user is logged in via an authentication provider, they will remain
# logged in via the use of cookies. By default, this cookie will last one year.
# This is managed by `flask_login`, but is copied here for convenience.
# For other options regarding sessions, please refer to:
# https://flask-login.readthedocs.io/en/latest/#cookie-settings
REMEMBER_COOKIE_DURATION = datetime.timedelta(days=365)

# ---------------------------------------------------
# Policy configuration
# ---------------------------------------------------
# This section configures various policy related to access control.

# Should anonymous users be able to view the post indices
POLICY_ANONYMOUS_VIEW_INDEX = True

# Should anonymous users be able to view the content of posts
POLICY_ANONYMOUS_VIEW_POST = True

# Should anonymous users be able to view overall statistics
POLICY_ANONYMOUS_VIEW_STATS = True

# Should anonymous users be able to download posts (or their source)
POLICY_ANONYMOUS_DOWNLOADS = False


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
# Repository Indexing configuration
# ---------------------------------------------------
# The Knowedge Repo updates the index of available posts on a regular basis.
# If the database is not thread-safe (i.e. in the case of SQLite), then the
# index will be updated on the main thread before every request that is more
# than `INDEX_INTERVAL` seconds after the last sync completed. Otherwise,
# indexing will occur every `INDEX_INTERVAL` seconds after the previous sync.
# Syncing is designed to be compatible with multiple instances of the Knowledge
# Repo connected to the same database, accross multiple machines and/or
# processes; and so a global indexing lock is employed. When a sync begins,
# a sync lock is put in place and the responsible process is considered to be
# the primary agent responsible for syncing until its last update is longer than
# `INDEXING_TIMEOUT` seconds, whereby the lock is ceded to the next requesting
# process. Note that `INDEXING_TIMEOUT` must be larger than `INDEXING_INTERVAL`
# or strange things might begin to happen.
INDEXING_INTERVAL = 5 * 60  # 5 minutes
INDEXING_TIMEOUT = 10 * 60  # 10 minutes

# Whether an index operation should update repositories
INDEXING_UPDATES_REPOSITORIES = True

# Whether repositories should be updated even without a sync lock (in which case
# the repositories will be updated on the sync timers, even if the relevant
# process/thread does not have a lock on updating the index). This is useful in
# context of multiple Knowledge Repo servers working together to serve the
# repositories across multiple machines, which each require repository syncing.
# Disable this if (for some reason) you have multiple Knowledge Repo servers
# running on the same machine, and you want to avoid potential clashes. This
# key is ignored if `INDEXING_UPDATES_REPOSITORIES` is False
INDEXING_UPDATES_REPOSITORIES_WITHOUT_LOCK = True

# In some cases you may want to disable indexing entirely, which is currently
# only ever used by the Knowledge Post previewer. Disabling the index means that
# posts will not be discoverable, but if know the path in the repository you can
# view the post with a direct link.
INDEXING_ENABLED = True

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
