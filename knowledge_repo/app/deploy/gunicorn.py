""" gunicorn.py

    Utilities for running the knowledge app via gunicorn.

    Adapted from example in http://docs.gunicorn.org/en/stable/custom.html.
"""

from __future__ import absolute_import

from gunicorn.app.base import BaseApplication

from .common import KnowledgeDeployer


class GunicornDeployer(BaseApplication, KnowledgeDeployer):

    _registry_keys = ['gunicorn']

    def __init__(self, *args, **kwargs):
        KnowledgeDeployer.__init__(self, *args, **kwargs)
        BaseApplication.__init__(self)

    def load_config(self):
        options = {
            'bind': '{}:{}'.format(self.host, self.port),
            'workers': self.workers,
            'timeout': self.timeout
        }
        for key, value in options.items():
            self.cfg.set(key, value)

    def load(self):
        return self.builder_func()

    def run(self):
        if not self.app.supports_threads:
            raise RuntimeError("Database configuration is not suitable for deployment (not thread-safe).")
        return BaseApplication.run(self)
