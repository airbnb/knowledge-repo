from __future__ import absolute_import
from __future__ import print_function

from builtins import object
import sys
import os
import posixpath
from abc import abstractmethod, abstractproperty
import datetime
from collections import OrderedDict
from enum import Enum
import uuid

from . import config_defaults
from .post import KnowledgePost
from .config import KnowledgeRepositoryConfig
from .postprocessor import KnowledgePostProcessor
from .utils.registry import SubclassRegisteringABCMeta
from future.utils import with_metaclass

if sys.version_info.major > 2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


class KnowledgeRepository(with_metaclass(SubclassRegisteringABCMeta, object)):
    _registry_keys = None

    class PostStatus(Enum):
        '''
        Do not store these values in a datastore, as they may change
        from release to release. These keys should only be used to compare with
        the output of a KnowledgeRepository.
        '''
        DRAFT = 0  # Post is still being written and not yet submitted
        SUBMITTED = 1  # Post is submitted and waiting for review
        UNPUBLISHED = 2  # Post is approved to publish, but not published
        PUBLISHED = 3  # Post is published and visible on /feed

    @classmethod
    def for_uri(cls, uri, *args, **kwargs):
        if isinstance(uri, dict):
            return cls.for_uris(uri)
        scheme = urlparse(uri).scheme
        return cls._get_subclass_for(scheme)(uri, *args, **kwargs)

    @classmethod
    def for_uris(cls, uri):
        # Import this within this method so as not to cause import resolution problems
        from .repositories.meta import MetaKnowledgeRepository
        if isinstance(uri, str):
            uris = {'': uri}
        else:
            uris = uri

        krs = {name: cls.for_uri(uri) for name, uri in list(uris.items())}
        return MetaKnowledgeRepository(krs)

    @classmethod
    def create_for_uri(cls, uri, **kwargs):
        if isinstance(uri, dict):
            return cls.for_uris(uri)
        scheme = urlparse(uri).scheme
        return cls._get_subclass_for(scheme).create(uri, **kwargs)

    @classmethod
    def create(cls, uri, **kwargs):
        raise NotImplementedError

    def __init__(self, uri, debug=False, **kwargs):
        self.uri = uri
        self.config = KnowledgeRepositoryConfig()
        self.config.debug = debug
        self.config.update_defaults(config_defaults)
        self.init(**kwargs)

    def init(self):
        pass

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        assert isinstance(config, KnowledgeRepositoryConfig), "`config` should be a `KnowledgeRepositoryConfig` instance."
        self._config = config

    @property
    def uris(self):
        # This translates KnowledgeRepository.uri to a consistent format
        # across all KnowledgeRepository instances: a dictionary of form
        # {<mountpoint>: <uri>}
        # It assumes that self.uri is either a string or a dictionary mapping
        # of form:
        # {<mountpoint>: <KnowledgeRepositoryInstance>}
        if isinstance(self.uri, str):
            return {'': self.uri}
        elif isinstance(self.uri, dict):
            uri_dict = {}

            def add_uris(uri_dict, uris, parent=''):
                assert isinstance(uris, dict)
                for mountpoint, uri in uris.items():
                    if isinstance(uri, (str, KnowledgeRepository)):
                        uri_dict[posixpath.join(parent, mountpoint)] = uri if isinstance(uri, str) else uri.uri
                    elif isinstance(uri, dict):
                        add_uris(uri_dict, uri, parent=posixpath.join(parent, mountpoint))
                    else:
                        raise ValueError("Unrecognised uri: {}".format(uri))
            add_uris(uri_dict, self.uri)
            return uri_dict
        raise ValueError("Unrecognised KnowledgeRepository.uri: {}".format(self.uri))

    # ------------- Repository actions / state ------------------------------------

    def session_begin(self):
        pass

    def session_end(self):
        pass

    @abstractproperty
    def revision(self):
        raise NotImplementedError

    def update(self):
        pass

    @abstractproperty
    def status(self):
        raise NotImplementedError

    @abstractproperty
    def status_message(self):
        raise NotImplementedError

    def set_active_draft(self, path):
        pass

    # -------------- Post retrieval methods --------------------------------------

    def post(self, path, revision=None):
        path = self._kp_path(path)
        if not self.has_post(path, revision=revision) and path in self.config.aliases:
            path = self.config.aliases[path]
            if path in self.config.alias:
                raise ValueError("Alias cycle detected.")
        assert self.has_post(path, revision=revision), "{} does not have a post for path '{}'.".format(self.__class__.__name__, path)
        return KnowledgePost(path=path, repository=self, revision=revision or self._kp_get_revision(path))

    def dir(self, prefix=None, status=None):
        if prefix is None or isinstance(prefix, str):
            prefixes = [prefix]
        else:
            prefixes = prefix
        assert all([prefix is None or isinstance(prefix, str) for prefix in prefixes]), "All path prefixes must be strings."
        prefixes = [prefix if prefix is None else posixpath.relpath(prefix, '/') for prefix in prefixes]
        if isinstance(status, str):
            if status == 'all':
                status = [self.PostStatus.DRAFT, self.PostStatus.SUBMITTED, self.PostStatus.PUBLISHED, self.PostStatus.UNPUBLISHED]
            else:
                raise ValueError('Status alias `{}` not recognised.'.format(status))
        if status is not None and not isinstance(status, list):
            status = [status]
        elif status is None:
            status = [self.PostStatus.PUBLISHED]

        # Use old syntax for "yielding from" to maintain support for python 2
        for prefix in prefixes:
            for path in self._dir(prefix=prefix, statuses=status):
                yield path

    @abstractmethod
    def _dir(self, prefix, statuses):
        raise NotImplementedError

    def has_post(self, path, revision=None):
        return self._kp_exists(self._kp_path(path), revision=revision)

    def post_status(self, path, revision=None, detailed=False):
        return self._kp_status(self._kp_path(path), revision=revision, detailed=detailed)

    def post_statuses(self, paths, detailed=False):
        return OrderedDict([(path, self.post_status(path, detailed=detailed)) for path in paths])

    def posts(self, status=None, only_valid=False):
        for path in self.dir(status=status):
            post = self.post(path)
            if only_valid and not post.is_valid():
                continue
            yield post

    def __getitem__(self, path):
        return self.post(path)

    def __len__(self):
        return len(self.dir())

    def __iter__(self):
        return self.posts()

    def __contains__(self, path):
        return self.has_post(path)

    # -------------- Post submission / addition user flow --------------------

    def add(self, kp, path=None, update=False, **kwargs):  # Create a new knowledge post draft
        assert isinstance(kp, KnowledgePost), "One can only add KnowledgePost objects to a KnowledgeRepository."
        path = path or kp.path
        if not path:
            raise ValueError("Post path not provided for Knowledge Post, and one is not specified within the knowledge post. Either add the path to post headers using `path: <path>` or specify the project path on the command line adding `-p <path>` to the current command.")
        path = self._kp_path(path)
        path = self.config.path_parse(path)

        current_datetime = datetime.datetime.now()
        authors = kp.headers['authors']
        new_authors = [self.config.username_parse(author) for author in authors]
        if new_authors != authors or kp.headers['updated_at'] < current_datetime:
            kp.update_headers(authors=new_authors, updated_at=current_datetime)

        for postprocessor in self.config.postprocessors:
            KnowledgePostProcessor._get_subclass_for(postprocessor).process(kp)

        cleanup_kwargs = self._add_prepare(kp, path, update, **kwargs)

        self._kp_save(kp, path, update=update)

        if cleanup_kwargs:
            kwargs.update(cleanup_kwargs)
        self._add_cleanup(kp, path, update, **kwargs)

        return kp

    @abstractmethod
    def _add_prepare(self, kp, path, update=False):
        raise NotImplementedError

    @abstractmethod
    def _add_cleanup(self, kp, path, update=False):
        raise NotImplementedError

    def revise(self, kp, path, **kwargs):
        return self.add(kp, path, update=True, **kwargs)

    def submit(self, path):  # Submit a post for review
        return self._submit(self._kp_path(path))

    @abstractmethod
    def _submit(self, path):  # Submit a post for review
        raise NotImplementedError

    def accept(self, path):  # Submit a post for review
        return self._accept(self._kp_path(path))

    @abstractmethod
    def _accept(self, path):  # Submit a post for review
        raise NotImplementedError

    def publish(self, path):  # Publish a post for general perusal
        return self._publish(self._kp_path(path))

    @abstractmethod
    def _publish(self, path):  # Publish a post for general perusal
        raise NotImplementedError

    def unpublish(self, path):  # Unpublish a post for general perusal
        return self._unpublish(self._kp_path(path))

    @abstractmethod
    def _unpublish(self, path):  # Unpublish a post for general perusal
        raise NotImplementedError

    def remove(self, path, all=False):
        return self._remove(self._kp_path(path), all=all)

    @abstractmethod
    def _remove(self, path, all=False):
        raise NotImplementedError

    # ----------- Knowledge Post Data Retrieval/Pushing Methods --------------------

    def _kp_repository_uri(self, path):
        return self.uri

    @abstractmethod
    def _kp_uuid(self, path):
        raise NotImplementedError

    def _kp_path(self, path, rel='/'):
        if path is None:
            return None
        path = os.path.relpath(os.path.abspath(os.path.join(rel, path)), rel)
        if os.name == 'nt':
            path = path.replace(os.path.sep, os.path.altsep)
        assert all([not segment.endswith('.kp') for segment in path.split(
            '/')[:-1]]), "The post path may not contain a directory named '*.kp'."
        if path == '.' or path.startswith('..'):
            raise ValueError("Provided path '{}' is outside of the knowledge repository.".format(path))
        if not path.endswith('.kp'):
            path += '.kp'
        return path

    @abstractmethod
    def _kp_exists(self, path, revision=None):
        raise NotImplementedError

    @abstractmethod
    def _kp_status(self, path, revision=None, detailed=False):
        raise NotImplementedError

    @abstractmethod
    def _kp_get_revision(self, path, status=None):
        raise NotImplementedError

    @abstractmethod
    def _kp_get_revisions(self, path):
        raise NotImplementedError

    @abstractmethod
    def _kp_read_ref(self, path, reference, revision=None):
        raise NotImplementedError

    @abstractmethod
    def _kp_dir(self, path, parent=None, revision=None):
        raise NotImplementedError

    @abstractmethod
    def _kp_has_ref(self, path, reference, revision=None):
        raise NotImplementedError

    @abstractmethod
    def _kp_diff(self, path, head, base):
        raise NotImplementedError

    @abstractmethod
    def _kp_write_ref(self, path, reference, data, uuid=None, revision=None):
        raise NotImplementedError

    @abstractmethod
    def _kp_new_revision(self, path, uuid=None):
        raise NotImplementedError

    def _kp_web_uri(self, path):
        return self.config.web_uri(path)

    def _kp_save(self, kp, path, update=False):
        if not update and self.has_post(path):
            raise ValueError("A knowledge post with the same path already exists. To update it, set the update flag.")
        kp.uuid = self._kp_uuid(path) or kp.uuid
        kp.path = path
        kp.revision = self._kp_new_revision(path, uuid=kp.uuid)
        kp.repository = self

        for ref in kp._dir():
            self._kp_write_ref(path, ref, kp._read_ref(ref), uuid=kp.uuid, revision=kp.revision)

    @property
    def web_uri(self):
        return self.config.web_uri()

    # ----------- Interface with web app ----------------------------------
    def get_app(self, *args, **kwargs):
        from . import app
        return self.config.prepare_app(app.KnowledgeFlask(self, *args, **kwargs))
