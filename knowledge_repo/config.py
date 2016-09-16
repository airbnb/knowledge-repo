import imp
import types
import logging
import os
import time

logger = logging.getLogger(__name__)


class KnowledgeRepositoryConfig(dict):

    def __init__(self, *args, **kwargs):
        super(KnowledgeRepositoryConfig, self).__init__(*args, **kwargs)
        self.DEFAULT_CONFIGURATION = {}

    def __getitem__(self, key):
        try:
            return super(KnowledgeRepositoryConfig, self).__getitem__(key)
        except:
            return self.DEFAULT_CONFIGURATION[key]

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def __dir__(self):
        return list(set(list(self.DEFAULT_CONFIGURATION.keys()) + list(self.keys())))

    def update(self, *values, **kwargs):
        for value in values:
            if isinstance(value, dict):
                if 'DEFAULT_CONFIGURATION' in value:
                    value = value.copy()
                    value.pop('DEFAULT_CONFIGURATION')
                dict.update(self, value)
            elif isinstance(value, types.ModuleType):
                self.__update_from_module(value)
            elif type(value) == str:
                if os.path.exists(value):
                    self.__update_from_file(value)
                else:
                    logger.warning(
                        "Configuration file {} does not exist.".format(value))
            elif isinstance(value, type(None)):
                pass
            else:
                raise ValueError("Cannot interpret {}".format(value))
        dict.update(self, kwargs)

    def update_defaults(self, *values, **kwargs):
        for value in values:
            if type(value) == dict:
                self.DEFAULT_CONFIGURATION.update(value)
            elif isinstance(value, types.ModuleType):
                self.__defaults_from_module(value)
            elif type(value) == str:
                if os.path.exists(value):
                    self.__defaults_from_file(value)
                else:
                    logger.warning("Configuration file {} does not exist.".format(value))
            elif isinstance(value, type(None)):
                pass
            else:
                raise ValueError("Cannot interpret {}".format(value))
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
        config = imp.load_source('knowledge_repo.config_{}'.format(str(time.time()).replace('.', '')), filename)
        self.__set_from_module(d, config, force)

    def __set_from_module(self, d, module, force=False):
        for key in dir(module):
            if not key.startswith('_'):
                if not force and key not in self.DEFAULT_CONFIGURATION:
                    logger.debug(
                        "Ignoring configuration key `{}` which is not a valid configuration key.".format(key))
                else:
                    d[key] = getattr(module, key)
