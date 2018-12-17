import functools
import imp
import logging
import os
import time
import types
import yaml

import six

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
        return list(set(list(self.DEFAULT_CONFIGURATION.keys()) + list(self.keys())))

    def update(self, *values, **kwargs):
        for value in values:
            if isinstance(value, dict):
                value = value.copy()
                value.pop('DEFAULT_CONFIGURATION', None)
                value.pop('_repo', None)
                dict.update(self, value)
            elif isinstance(value, types.ModuleType):
                self.__update_from_module(value)
            elif isinstance(value, six.string_types):
                if os.path.exists(value):
                    self.__update_from_file(value)
                else:
                    logger.warning(
                        u"Configuration file {} does not exist.".format(value))
            elif isinstance(value, type(None)):
                pass
            else:
                raise ValueError(u"Cannot interpret {}".format(value))
        dict.update(self, kwargs)

    def update_defaults(self, *values, **kwargs):
        for value in values:
            if type(value) == dict:
                self.DEFAULT_CONFIGURATION.update(value)
            elif isinstance(value, types.ModuleType):
                self.__defaults_from_module(value)
            elif isinstance(value, six.string_types):
                if os.path.exists(value):
                    self.__defaults_from_file(value)
                else:
                    logger.warning(u"Configuration file {} does not exist.".format(value))
            elif isinstance(value, type(None)):
                pass
            else:
                raise ValueError(u"Cannot interpret {}".format(value))
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
        if filename.endswith('.py'):
            config = imp.load_source(u'knowledge_repo.config_{}'.format(str(time.time()).replace('.', '')), filename)
            self.__set_from_module(d, config, force)
        elif filename.endswith('.yml'):
            with open(filename) as f:
                config = yaml.safe_load(f)
            self.update(config)

    def __set_from_module(self, d, module, force=False):
        for key in dir(module):
            if not key.startswith('_'):
                if not force and key not in self.DEFAULT_CONFIGURATION:
                    logger.debug(
                        "Ignoring configuration key `{}` which is not a valid configuration key.".format(key))
                else:
                    d[key] = getattr(module, key)
