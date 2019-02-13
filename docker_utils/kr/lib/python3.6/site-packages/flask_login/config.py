# -*- coding: utf-8 -*-
'''
    flask_login.config
    ------------------
    This module provides default configuration values.
'''


from datetime import timedelta


#: The default name of the "remember me" cookie (``remember_token``)
COOKIE_NAME = 'remember_token'

#: The default time before the "remember me" cookie expires (365 days).
COOKIE_DURATION = timedelta(days=365)

#: Whether the "remember me" cookie requires Secure; defaults to ``None``
COOKIE_SECURE = None

#: Whether the "remember me" cookie uses HttpOnly or not; defaults to ``False``
COOKIE_HTTPONLY = False

#: The default flash message to display when users need to log in.
LOGIN_MESSAGE = u'Please log in to access this page.'

#: The default flash message category to display when users need to log in.
LOGIN_MESSAGE_CATEGORY = 'message'

#: The default flash message to display when users need to reauthenticate.
REFRESH_MESSAGE = u'Please reauthenticate to access this page.'

#: The default flash message category to display when users need to
#: reauthenticate.
REFRESH_MESSAGE_CATEGORY = 'message'

#: The default attribute to retreive the unicode id of the user
ID_ATTRIBUTE = 'get_id'

#: Default name of the auth header (``Authorization``)
AUTH_HEADER_NAME = 'Authorization'

#: A set of session keys that are populated by Flask-Login. Use this set to
#: purge keys safely and accurately.
SESSION_KEYS = set(['user_id', 'remember', '_id', '_fresh', 'next'])

#: A set of HTTP methods which are exempt from `login_required` and
#: `fresh_login_required`. By default, this is just ``OPTIONS``.
EXEMPT_METHODS = set(['OPTIONS'])

#: If true, the page the user is attempting to access is stored in the session
#: rather than a url parameter when redirecting to the login view; defaults to
#: ``False``.
USE_SESSION_FOR_NEXT = False
