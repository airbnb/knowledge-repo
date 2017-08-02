from future.moves.urllib.parse import urlparse, urlencode, urljoin

from flask import request, url_for
from flask_login import AnonymousUserMixin
from flask_principal import UserNeed

from .. import roles
from ..proxies import current_app


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

    else:
        identity.provides.add(UserNeed(user.identifier))
        identity.provides.add(roles.index_view)
        identity.provides.add(roles.post_comment)
        identity.provides.add(roles.post_view)
        identity.provides.add(roles.post_download)
        identity.provides.add(roles.post_edit)
        identity.provides.add(roles.stats_view)

        # TODO: Populate group permissions, and port existing group admin
        # code to roles.

    return identity
