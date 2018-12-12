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
        env_args = self.cfg.parser().parse_args(self.cfg.get_cmd_args_from_env())

        # Load up environment configuration.
        for key, value in vars(env_args).items():
            if key != 'args' and value is not None:
                self.cfg.set(key, value)

        # Update the configuration with the options specified via KnowledgeDeployer
        options = {
            'bind': u'{}:{}'.format(self.host, self.port),
            'workers': self.workers,
            'timeout': self.timeout,
        }
        if self.app.config['DEPLOY_HTTPS']:
            options['certfile'] = self.app.config['SSL_CERT']['cert']
            options['keyfile'] = self.app.config['SSL_CERT']['key']
        for key, value in options.items():
            self.cfg.set(key, value)

    def load(self):
        if not self.app.check_thread_support():
            raise RuntimeError("Database configuration is not suitable for deployment (not thread-safe).")
        return self.app.start_indexing()
