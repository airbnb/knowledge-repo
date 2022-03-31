from .constants import PY_EXTENSION, YML_EXTENSION
from .utils.files import read_yaml

import functools
import importlib
import logging
import os
import sys
import time
import types

logger = logging.getLogger(__name__)


class KnowledgeRepositoryConfig(dict):

    def __init__(self, repo, *args, **kwargs):
        self._repo = repo
        super(KnowledgeRepositoryConfig, self).__init__(*args, **kwargs)
        self.DEFAULT_CONFIGURATION = {}

    def __getitem__(self, key):
        try:
            value = super(KnowledgeRepositoryConfig, self).__getitem__(key)
        except KeyError:
            value = self.DEFAULT_CONFIGURATION[key]
        if isinstance(value, types.FunctionType):
            value = functools.partial(value, self._repo)
        return value

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def __dir__(self):
        return list(set(
            list(self.DEFAULT_CONFIGURATION.keys()) + list(self.keys())))

    def update(self, *values, **kwargs):
        for value in values:
            if isinstance(value, dict):
                value = value.copy()
                value.pop('DEFAULT_CONFIGURATION', None)
                value.pop('_repo', None)
                dict.update(self, value)
            elif isinstance(value, types.ModuleType):
                self.__update_from_module(value)
            elif isinstance(value, str):
                if os.path.exists(value):
                    self.__update_from_file(value)
                else:
                    logger.warning(
                        f'Configuration file {value} does not exist.')
            elif isinstance(value, type(None)):
                pass
            else:
                raise ValueError(f'Cannot interpret {value}')
        dict.update(self, kwargs)

    def update_defaults(self, *values, **kwargs):
        for value in values:
            if type(value) == dict:
                self.DEFAULT_CONFIGURATION.update(value)
            elif isinstance(value, types.ModuleType):
                self.__defaults_from_module(value)
            elif isinstance(value, str):
                if os.path.exists(value):
                    self.__defaults_from_file(value)
                else:
                    logger.warning(
                        f'Configuration file {value} does not exist.')
            elif isinstance(value, type(None)):
                pass
            else:
                raise ValueError(f'Cannot interpret {value}')
        self.DEFAULT_CONFIGURATION.update(kwargs)

    def __defaults_from_file(self, filename):
        self.__set_from_file(self.DEFAULT_CONFIGURATION, filename, force=True)

    def __update_from_file(self, filename):
        self.__set_from_file(self, filename)

    def __defaults_from_module(self, module):
        self.__set_from_module(self.DEFAULT_CONFIGURATION, module, force=True)

    def __update_from_module(self, module):
        self.__set_from_module(self, module)

    def __set_from_file(self, d, filename, force=False):
        if filename.endswith(PY_EXTENSION):
            time_str = str(time.time()).replace('.', '')
            module_name = f'knowledge_repo.config_{time_str}'
            spec = importlib.util.spec_from_file_location(
                module_name, filename)
            config = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            self.__set_from_module(d, config, force)
        elif filename.endswith(YML_EXTENSION):
            config = read_yaml(filename)
            self.update(config)

    def __set_from_module(self, d, module, force=False):
        for key in dir(module):
            if not key.startswith('_'):
                if not force and key not in self.DEFAULT_CONFIGURATION:
                    logger.debug(
                        f'Ignoring configuration key `{key}` '
                        'which is not a valid configuration key.')
                else:
                    d[key] = getattr(module, key)
