from builtins import object

import os
from functools import wraps

from .postprocessor import KnowledgePostProcessor
from .utils.registry import SubclassRegisteringABCMeta
from .utils.dependencies import check_dependencies
from future.utils import with_metaclass


def get_format(filename, format=None):
    if format is None:
        format = os.path.splitext(filename)[1]
        if format.startswith('.'):
            format = format[1:]
    return format


class KnowledgePostConverter(with_metaclass(SubclassRegisteringABCMeta, object)):
    _registry_keys = None  # File extensions

    def __init__(self, kp, format=None, postprocessors=None, **kwargs):
        check_dependencies(self.dependencies, "Whoops! You are missing some dependencies required to use `{}` instances.".format(self.__class__.__name__))
        self.kp = kp
        self.format = format
        if postprocessors is None:
            postprocessors = ['extract_images', 'format_checks']
        self.postprocessors = postprocessors
        self.init(**kwargs)

    @property
    def dependencies(self):
        return []

    def init(self):
        pass

    def __get_wrapped_with_postprocessors(self, f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            kp = self.kp
            f(*args, **kwargs)
            postprocessors = self.postprocessors

            if f.__name__ == 'from_file':
                filename = args[0] if len(args) > 0 else kwargs['filename']
                kp.orig_context = os.path.dirname(filename)

            if postprocessors is None:
                postprocessors = []
            for postprocessor in postprocessors:
                KnowledgePostProcessor._get_subclass_for(postprocessor).process(kp)

            return kp
        return wrapped

    def __getattribute__(self, attr):
        if attr in ['from_file', 'from_string']:
            return self.__get_wrapped_with_postprocessors(object.__getattribute__(self, attr))
        return object.__getattribute__(self, attr)

    def from_file(self, filename, **opts):
        raise NotImplementedError

    def from_string(self, string, **opts):
        raise NotImplementedError

    def to_file(self, filename, **opts):
        raise NotImplementedError

    def to_string(self, **opts):
        raise NotImplementedError

    @classmethod
    def for_file(cls, kp, filename, format=None, postprocessors=None):
        return cls.for_format(kp, get_format(filename, format), postprocessors=postprocessors)

    @classmethod
    def for_format(cls, kp, format, postprocessors=None):
        if format.lower() not in cls._registry:
            raise ValueError("The knowledge repository does not support files of type '{}'. Supported types are: {}."
                             .format(format, ','.join(list(cls._registry.keys()))))
        return cls._get_subclass_for(format.lower())(kp, format=format, postprocessors=postprocessors)
