from future.moves.urllib.parse import urlparse, urlencode
from urlparse import urlparse, urljoin

from flask import request, url_for
from flask_login import AnonymousUserMixin


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
