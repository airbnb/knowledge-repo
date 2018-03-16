import datetime

from future.moves.urllib.parse import urlparse, urlencode, urljoin

from flask import request, url_for
from flask_login import AnonymousUserMixin, login_user
from flask_principal import Identity, identity_changed, UserNeed

from .. import roles
from ..proxies import current_app, db_session


def prepare_user(user, session_start=True):
    cache_lifetime = current_app.config['AUTH_USER_ATTRIBUTE_CACHE_LIFETIME'] or 0
    if (
        current_app.config['AUTH_USER_ATTRIBUTE_SETTER'] and
        (
            session_start or
            user.last_login_at is None or
            user.last_login_at < datetime.datetime.now() - datetime.timedelta(seconds=cache_lifetime)
        )
    ):
        session_start = True
        user = current_app.config['AUTH_USER_ATTRIBUTE_SETTER'](user)

    if session_start or user.id is None:
        user.last_login_at = datetime.datetime.now()
        db_session.add(user)
        db_session.commit()

    return user


class AnonymousKnowledgeUser(AnonymousUserMixin):
    id = None
    identifier = None
    created_at = None
    posts = []

    @property
    def subscriptions(self):
        return []

    @property
    def liked_posts(self):
        return []


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def populate_identity_roles(identity, user=None):
    identity.user = user

    if user is None or user.is_anonymous:
        if current_app.config['POLICY_ANONYMOUS_VIEW_INDEX']:
            identity.provides.add(roles.index_view)
        if current_app.config['POLICY_ANONYMOUS_VIEW_POST']:
            identity.provides.add(roles.post_view)
        if current_app.config['POLICY_ANONYMOUS_VIEW_STATS']:
            identity.provides.add(roles.stats_view)
        if current_app.config['POLICY_ANONYMOUS_DOWNLOADS']:
            identity.provides.add(roles.post_download)

    else:
        identity.provides.add(UserNeed(user.identifier))
        identity.provides.add(roles.index_view)
        identity.provides.add(roles.post_view)
        identity.provides.add(roles.post_edit)
        identity.provides.add(roles.post_comment)
        identity.provides.add(roles.post_download)
        identity.provides.add(roles.stats_view)

        # TODO: Populate group permissions, and port existing group admin
        # code to roles.

    return identity
