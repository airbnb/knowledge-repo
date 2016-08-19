# This file is only needed for setting up a dedicated server configuration
# with support for extracting username information and emailing users.

import os


SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'knowledge.db')


# ---------------------------------------------------
# Authentication Headers
# ---------------------------------------------------
# the username request header should allow you to get
# a person's username - this is used for pageview tracking,
# likes, favorites, etc. As a fallback, DEFAULT_USER is used.
AUTH_USERNAME_REQUEST_HEADER = 'test_user_request_header'
AUTH_USERNAME_DEFAULT = 'knowledge_default'
# DEFAULT_USER = 'knowledge_default'

# the group request header should allow you to get a
# user's name. This is then used below, where we can
# map specific users to specific projects for the
# webeditor posts
AUTH_GROUP_REQUEST_HEADER = 'test_group_request_header'
AUTH_GROUP_DEFAULT = ''

USER_GROUP_TO_PROJECT = {}

# Make sure the mail app does not send
TESTING = True

MAIL_SERVER = 'localhost'
MAIL_DEFAULT_SENDER = "knowledge_editors"
MAIL_DEFAULT_RECIPIENT = "knowledge_consumers"
MAIL_ADDRESS_EXTENSION = '@example.com'

SERVER_NAME = 'localhost'


def MAIL_USERNAMES_TO_EMAILS(x):
    return x
