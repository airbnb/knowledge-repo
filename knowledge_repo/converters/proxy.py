import re

from ..converter import KnowledgePostConverter


class ProxyConverter(KnowledgePostConverter):

    _registry_keys = ['proxy']

    def from_file(self, url, **opts):

        # Deal with special cases, whereby url should be mutated before being
        # added to post headers.

        # Google presentations should be embedded in "embed" mode.
        gpres = re.match('^https://docs.google.com/presentation/d/(?P<pres_id>[^/]+)/edit(?P<slide_query>.*)$', url)
        if gpres:
            url = "https://docs.google.com/presentation/d/{}/embed{}".format(*gpres.groups())

        self.kp_write("", headers={'proxy': url})
