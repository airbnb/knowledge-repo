""" gunicorn.py

    Utilities for running the knowledge app via gunicorn.

    Adapted from example in http://docs.gunicorn.org/en/stable/custom.html.
"""

from .common import KnowledgeDeployer
from gunicorn.app.base import BaseApplication
import importlib.machinery
import importlib.util
import os
import sys
import traceback
import warnings


class GunicornDeployer(BaseApplication, KnowledgeDeployer):

    _registry_keys = ['gunicorn']

    def __init__(self, *args, **kwargs):
        KnowledgeDeployer.__init__(self, *args, **kwargs)
        BaseApplication.__init__(self)

    def load_config(self):
        env_args = self.cfg.parser().parse_args(
            self.cfg.get_cmd_args_from_env())

        if env_args.config:
            self.load_config_from_filename(env_args.config)

        # Load up environment configuration.
        for key, value in vars(env_args).items():
            if key != 'args' and value is not None:
                self.cfg.set(key, value)

        # Update the configuration with the options specified
        # via KnowledgeDeployer
        options = {
            'bind': f'{self.host}:{self.port}',
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
            raise RuntimeError('Database configuration is not suitable '
                               'for deployment (not thread-safe).')
        return self.app.start_indexing()

    def load_config_from_filename(self, filename):
        """
        Loads the configuration file: the file is a
        python file, otherwise raise an RuntimeError
        Exception or stop the process if the configuration
        file contains a syntax error.
        """

        if not os.path.exists(filename):
            raise RuntimeError("%r doesn't exist" % filename)

        ext = os.path.splitext(filename)[1]

        try:
            module_name = '__config__'
            if ext in ['.py', '.pyc']:
                spec = importlib.util.spec_from_file_location(
                    module_name, filename)
            else:
                warnings.warn('configuration file should have '
                              'a valid Python extension.\n')
                loader_ = importlib.machinery.SourceFileLoader(
                    module_name, filename)
                spec = importlib.util.spec_from_file_location(
                    module_name, filename, loader=loader_)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)
        except Exception:
            print(f'Failed to read config file: {filename}', file=sys.stderr)
            traceback.print_exc()
            sys.stderr.flush()
            sys.exit(1)

        cfg = vars(mod)

        for k, v in cfg.items():
            # Ignore unknown names
            if k not in self.cfg.settings:
                continue
            try:
                self.cfg.set(k.lower(), v)
            except Exception:
                print(f'Invalid value for {k}: {v}\n', file=sys.stderr)
                sys.stderr.flush()
                raise

        return cfg
