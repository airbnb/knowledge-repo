# -*- coding: utf-8 -*-
'''
    flask_login.login_manager
    -------------------------
    The LoginManager class.
'''


import warnings
from datetime import datetime, timedelta

from flask import (_request_ctx_stack, abort, current_app, flash, redirect,
                   request, session)

from ._compat import text_type
from .config import (COOKIE_NAME, COOKIE_DURATION, COOKIE_SECURE,
                     COOKIE_HTTPONLY, LOGIN_MESSAGE, LOGIN_MESSAGE_CATEGORY,
                     REFRESH_MESSAGE, REFRESH_MESSAGE_CATEGORY, ID_ATTRIBUTE,
                     AUTH_HEADER_NAME, SESSION_KEYS, USE_SESSION_FOR_NEXT)
from .mixins import AnonymousUserMixin
from .signals import (user_loaded_from_cookie, user_loaded_from_header,
                      user_loaded_from_request, user_unauthorized,
                      user_needs_refresh, user_accessed, session_protected)
from .utils import (_get_user, login_url as make_login_url, _create_identifier,
                    _user_context_processor, encode_cookie, decode_cookie,
                    make_next_param, expand_login_view)


class LoginManager(object):
    '''This object is used to hold the settings used for logging in. Instances
    of :class:`LoginManager` are *not* bound to specific apps, so you can
    create one in the main body of your code and then bind it to your
    app in a factory function.
    '''
    def __init__(self, app=None, add_context_processor=True):
        #: A class or factory function that produces an anonymous user, which
        #: is used when no one is logged in.
        self.anonymous_user = AnonymousUserMixin

        #: The name of the view to redirect to when the user needs to log in.
        #: (This can be an absolute URL as well, if your authentication
        #: machinery is external to your application.)
        self.login_view = None

        #: Names of views to redirect to when the user needs to log in,
        #: per blueprint. If the key value is set to None the value of
        #: :attr:`login_view` will be used instead.
        self.blueprint_login_views = {}

        #: The message to flash when a user is redirected to the login page.
        self.login_message = LOGIN_MESSAGE

        #: The message category to flash when a user is redirected to the login
        #: page.
        self.login_message_category = LOGIN_MESSAGE_CATEGORY

        #: The name of the view to redirect to when the user needs to
        #: reauthenticate.
        self.refresh_view = None

        #: The message to flash when a user is redirected to the 'needs
        #: refresh' page.
        self.needs_refresh_message = REFRESH_MESSAGE

        #: The message category to flash when a user is redirected to the
        #: 'needs refresh' page.
        self.needs_refresh_message_category = REFRESH_MESSAGE_CATEGORY

        #: The mode to use session protection in. This can be either
        #: ``'basic'`` (the default) or ``'strong'``, or ``None`` to disable
        #: it.
        self.session_protection = 'basic'

        #: If present, used to translate flash messages ``self.login_message``
        #: and ``self.needs_refresh_message``
        self.localize_callback = None

        self.user_callback = None

        self.unauthorized_callback = None

        self.needs_refresh_callback = None

        self.id_attribute = ID_ATTRIBUTE

        self.header_callback = None

        self.request_callback = None

        self._session_identifier_generator = _create_identifier

        if app is not None:
            self.init_app(app, add_context_processor)

    def setup_app(self, app, add_context_processor=True):  # pragma: no cover
        '''
        This method has been deprecated. Please use
        :meth:`LoginManager.init_app` instead.
        '''
        warnings.warn('Warning setup_app is deprecated. Please use init_app.',
                      DeprecationWarning)
        self.init_app(app, add_context_processor)

    def init_app(self, app, add_context_processor=True):
        '''
        Configures an application. This registers an `after_request` call, and
        attaches this `LoginManager` to it as `app.login_manager`.

        :param app: The :class:`flask.Flask` object to configure.
        :type app: :class:`flask.Flask`
        :param add_context_processor: Whether to add a context processor to
            the app that adds a `current_user` variable to the template.
            Defaults to ``True``.
        :type add_context_processor: bool
        '''
        app.login_manager = self
        app.after_request(self._update_remember_cookie)

        self._login_disabled = app.config.get('LOGIN_DISABLED', False)

        if add_context_processor:
            app.context_processor(_user_context_processor)

    def unauthorized(self):
        '''
        This is called when the user is required to log in. If you register a
        callback with :meth:`LoginManager.unauthorized_handler`, then it will
        be called. Otherwise, it will take the following actions:

            - Flash :attr:`LoginManager.login_message` to the user.

            - If the app is using blueprints find the login view for
              the current blueprint using `blueprint_login_views`. If the app
              is not using blueprints or the login view for the current
              blueprint is not specified use the value of `login_view`.

            - Redirect the user to the login view. (The page they were
              attempting to access will be passed in the ``next`` query
              string variable, so you can redirect there if present instead
              of the homepage. Alternatively, it will be added to the session
              as ``next`` if USE_SESSION_FOR_NEXT is set.)

        If :attr:`LoginManager.login_view` is not defined, then it will simply
        raise a HTTP 401 (Unauthorized) error instead.

        This should be returned from a view or before/after_request function,
        otherwise the redirect will have no effect.
        '''
        user_unauthorized.send(current_app._get_current_object())

        if self.unauthorized_callback:
            return self.unauthorized_callback()

        if request.blueprint in self.blueprint_login_views:
            login_view = self.blueprint_login_views[request.blueprint]
        else:
            login_view = self.login_view

        if not login_view:
            abort(401)

        if self.login_message:
            if self.localize_callback is not None:
                flash(self.localize_callback(self.login_message),
                      category=self.login_message_category)
            else:
                flash(self.login_message, category=self.login_message_category)

        config = current_app.config
        if config.get('USE_SESSION_FOR_NEXT', USE_SESSION_FOR_NEXT):
            login_url = expand_login_view(login_view)
            session['next'] = make_next_param(login_url, request.url)
            redirect_url = make_login_url(login_view)
        else:
            redirect_url = make_login_url(login_view, next_url=request.url)

        return redirect(redirect_url)

    def user_loader(self, callback):
        '''
        This sets the callback for reloading a user from the session. The
        function you set should take a user ID (a ``unicode``) and return a
        user object, or ``None`` if the user does not exist.

        :param callback: The callback for retrieving a user object.
        :type callback: callable
        '''
        self.user_callback = callback
        return callback

    def header_loader(self, callback):
        '''
        This function has been deprecated. Please use
        :meth:`LoginManager.request_loader` instead.

        This sets the callback for loading a user from a header value.
        The function you set should take an authentication token and
        return a user object, or `None` if the user does not exist.

        :param callback: The callback for retrieving a user object.
        :type callback: callable
        '''
        self.header_callback = callback
        return callback

    def request_loader(self, callback):
        '''
        This sets the callback for loading a user from a Flask request.
        The function you set should take Flask request object and
        return a user object, or `None` if the user does not exist.

        :param callback: The callback for retrieving a user object.
        :type callback: callable
        '''
        self.request_callback = callback
        return callback

    def unauthorized_handler(self, callback):
        '''
        This will set the callback for the `unauthorized` method, which among
        other things is used by `login_required`. It takes no arguments, and
        should return a response to be sent to the user instead of their
        normal view.

        :param callback: The callback for unauthorized users.
        :type callback: callable
        '''
        self.unauthorized_callback = callback
        return callback

    def needs_refresh_handler(self, callback):
        '''
        This will set the callback for the `needs_refresh` method, which among
        other things is used by `fresh_login_required`. It takes no arguments,
        and should return a response to be sent to the user instead of their
        normal view.

        :param callback: The callback for unauthorized users.
        :type callback: callable
        '''
        self.needs_refresh_callback = callback
        return callback

    def needs_refresh(self):
        '''
        This is called when the user is logged in, but they need to be
        reauthenticated because their session is stale. If you register a
        callback with `needs_refresh_handler`, then it will be called.
        Otherwise, it will take the following actions:

            - Flash :attr:`LoginManager.needs_refresh_message` to the user.

            - Redirect the user to :attr:`LoginManager.refresh_view`. (The page
              they were attempting to access will be passed in the ``next``
              query string variable, so you can redirect there if present
              instead of the homepage.)

        If :attr:`LoginManager.refresh_view` is not defined, then it will
        simply raise a HTTP 401 (Unauthorized) error instead.

        This should be returned from a view or before/after_request function,
        otherwise the redirect will have no effect.
        '''
        user_needs_refresh.send(current_app._get_current_object())

        if self.needs_refresh_callback:
            return self.needs_refresh_callback()

        if not self.refresh_view:
            abort(401)

        if self.localize_callback is not None:
            flash(self.localize_callback(self.needs_refresh_message),
                  category=self.needs_refresh_message_category)
        else:
            flash(self.needs_refresh_message,
                  category=self.needs_refresh_message_category)

        config = current_app.config
        if config.get('USE_SESSION_FOR_NEXT', USE_SESSION_FOR_NEXT):
            login_url = expand_login_view(self.refresh_view)
            session['next'] = make_next_param(login_url, request.url)
            redirect_url = make_login_url(self.refresh_view)
        else:
            login_url = self.refresh_view
            redirect_url = make_login_url(login_url, next_url=request.url)

        return redirect(redirect_url)

    def reload_user(self, user=None):
        '''
        This set the ctx.user with the user object loaded by your customized
        user_loader callback function, which should retrieved the user object
        with the user_id got from session.

        Syntax example:
        from flask_login import LoginManager
        @login_manager.user_loader
        def any_valid_func_name(user_id):
            # get your user object using the given user_id,
            # if you use SQLAlchemy, for example:
            user_obj = User.query.get(int(user_id))
            return user_obj

        Reason to let YOU define this self.user_callback:
            Because we won't know how/where you will load you user object.
        '''
        ctx = _request_ctx_stack.top

        if user is None:
            user_id = session.get('user_id')
            if user_id is None:
                ctx.user = self.anonymous_user()
            else:
                if self.user_callback is None:
                    raise Exception(
                        "No user_loader has been installed for this "
                        "LoginManager. Refer to"
                        "https://flask-login.readthedocs.io/"
                        "en/latest/#how-it-works for more info.")
                user = self.user_callback(user_id)
                if user is None:
                    ctx.user = self.anonymous_user()
                else:
                    ctx.user = user
        else:
            ctx.user = user

    def _load_user(self):
        '''Loads user from session or remember_me cookie as applicable'''
        user_accessed.send(current_app._get_current_object())

        # first check SESSION_PROTECTION
        config = current_app.config
        if config.get('SESSION_PROTECTION', self.session_protection):
            deleted = self._session_protection()
            if deleted:
                return self.reload_user()

        # If a remember cookie is set, and the session is not, move the
        # cookie user ID to the session.
        #
        # However, the session may have been set if the user has been
        # logged out on this request, 'remember' would be set to clear,
        # so we should check for that and not restore the session.
        is_missing_user_id = 'user_id' not in session
        if is_missing_user_id:
            cookie_name = config.get('REMEMBER_COOKIE_NAME', COOKIE_NAME)
            header_name = config.get('AUTH_HEADER_NAME', AUTH_HEADER_NAME)
            has_cookie = (cookie_name in request.cookies and
                          session.get('remember') != 'clear')
            if has_cookie:
                return self._load_from_cookie(request.cookies[cookie_name])
            elif self.request_callback:
                return self._load_from_request(request)
            elif header_name in request.headers:
                return self._load_from_header(request.headers[header_name])

        return self.reload_user()

    def _session_protection(self):
        sess = session._get_current_object()
        ident = self._session_identifier_generator()

        app = current_app._get_current_object()
        mode = app.config.get('SESSION_PROTECTION', self.session_protection)

        # if the sess is empty, it's an anonymous user or just logged out
        # so we can skip this

        if sess and ident != sess.get('_id', None):
            if mode == 'basic' or sess.permanent:
                sess['_fresh'] = False
                session_protected.send(app)
                return False
            elif mode == 'strong':
                for k in SESSION_KEYS:
                    sess.pop(k, None)

                sess['remember'] = 'clear'
                session_protected.send(app)
                return True

        return False

    def _load_from_cookie(self, cookie):
        user_id = decode_cookie(cookie)
        if user_id is not None:
            session['user_id'] = user_id
            session['_fresh'] = False

        self.reload_user()

        if _request_ctx_stack.top.user is not None:
            app = current_app._get_current_object()
            user_loaded_from_cookie.send(app, user=_get_user())

    def _load_from_header(self, header):
        user = None
        if self.header_callback:
            user = self.header_callback(header)
        if user is not None:
            self.reload_user(user=user)
            app = current_app._get_current_object()
            user_loaded_from_header.send(app, user=_get_user())
        else:
            self.reload_user()

    def _load_from_request(self, request):
        user = None
        if self.request_callback:
            user = self.request_callback(request)
        if user is not None:
            self.reload_user(user=user)
            app = current_app._get_current_object()
            user_loaded_from_request.send(app, user=_get_user())
        else:
            self.reload_user()

    def _update_remember_cookie(self, response):
        # Don't modify the session unless there's something to do.
        if 'remember' not in session and \
                current_app.config.get('REMEMBER_COOKIE_REFRESH_EACH_REQUEST'):
            session['remember'] = 'set'

        if 'remember' in session:
            operation = session.pop('remember', None)

            if operation == 'set' and 'user_id' in session:
                self._set_cookie(response)
            elif operation == 'clear':
                self._clear_cookie(response)

        return response

    def _set_cookie(self, response):
        # cookie settings
        config = current_app.config
        cookie_name = config.get('REMEMBER_COOKIE_NAME', COOKIE_NAME)
        domain = config.get('REMEMBER_COOKIE_DOMAIN')
        path = config.get('REMEMBER_COOKIE_PATH', '/')

        secure = config.get('REMEMBER_COOKIE_SECURE', COOKIE_SECURE)
        httponly = config.get('REMEMBER_COOKIE_HTTPONLY', COOKIE_HTTPONLY)

        if 'remember_seconds' in session:
            duration = timedelta(seconds=session['remember_seconds'])
        else:
            duration = config.get('REMEMBER_COOKIE_DURATION', COOKIE_DURATION)

        # prepare data
        data = encode_cookie(text_type(session['user_id']))

        if isinstance(duration, int):
            duration = timedelta(seconds=duration)

        try:
            expires = datetime.utcnow() + duration
        except TypeError:
            raise Exception('REMEMBER_COOKIE_DURATION must be a ' +
                            'datetime.timedelta, instead got: {0}'.format(
                                duration))

        # actually set it
        response.set_cookie(cookie_name,
                            value=data,
                            expires=expires,
                            domain=domain,
                            path=path,
                            secure=secure,
                            httponly=httponly)

    def _clear_cookie(self, response):
        config = current_app.config
        cookie_name = config.get('REMEMBER_COOKIE_NAME', COOKIE_NAME)
        domain = config.get('REMEMBER_COOKIE_DOMAIN')
        path = config.get('REMEMBER_COOKIE_PATH', '/')
        response.delete_cookie(cookie_name, domain=domain, path=path)
