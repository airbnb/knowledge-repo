from __future__ import print_function

import os
import shutil
import logging
import time
from io import open

import six

from ..post import KnowledgePost
from ..repository import KnowledgeRepository
from ..utils.encoding import encode

logger = logging.getLogger(__name__)


class FolderKnowledgeRepository(KnowledgeRepository):
    _registry_keys = ['', 'file']

    TEMPLATES = {
        'README.md': os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates', 'repository_readme.md')),
        '.knowledge_repo_config.yml': os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates', 'repository_config.yml'))
    }

    @classmethod
    def create(cls, uri, embed_tooling=False):
        if uri.startswith('file://'):
            uri = uri[len('file://'):]
        path = os.path.abspath(uri)
        if not os.path.exists(path):
            os.makedirs(path)

        # Add README and configuration templates
        for filename, template in cls.TEMPLATES.items():
            target = os.path.join(path, filename)
            if not os.path.exists(target):
                shutil.copy(template, target)
            else:
                logger.warning("Not overriding existing file '{}'.".format(filename))
        return FolderKnowledgeRepository(path)

    @classmethod
    def from_uri(cls, uri, *args, **kwargs):
        """
        If this folder is actually a git repository, a `GitKnowledgeRepository`
        is returned instead, unless the folder knowledge repository is explicitly
        requested via the 'file://' protocol.
        """
        check_for_git = True
        if uri.startswith('file://'):
            check_for_git = False
            uri = uri[len('file://'):]
        if check_for_git and os.path.exists(os.path.join(uri, '.git')):
            from .gitrepository import GitKnowledgeRepository
            return GitKnowledgeRepository(uri, *args, **kwargs)
        return cls(uri, *args, **kwargs)

    def init(self, config='.knowledge_repo_config.yml', auto_create=False):
        self.auto_create = auto_create
        self.path = self.uri
        self.config.update(os.path.join(self.path, config))

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        assert isinstance(path, six.string_types), "The path specified must be a string."
        path = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(path):
            path = os.path.abspath(path)
            if self.auto_create:
                self.create(path)
            else:
                raise ValueError("Provided path '{}' does not exist.".format(path))
        self._path = path

    # ----------- Repository actions / state ------------------------------------
    @property
    def revision(self):
        return time.time()

    @property
    def status(self):
        return 'OK'

    @property
    def status_message(self):
        return 'OK'

    # ---------------- Post retrieval methods --------------------------------

    def _dir(self, prefix, statuses):
        posts = set()

        if self.PostStatus.PUBLISHED in statuses:

            for path, folders, files in os.walk(os.path.join(self.path, prefix or '')):

                # Do not visit hidden folders
                for folder in folders:
                    if folder.startswith('.'):
                        folders.remove(folder)

                posts.update(
                    os.path.join(os.path.relpath(path, start=self.path), folder)
                    for folder in folders if folder.endswith('.kp')
                )
                posts.update(
                    os.path.join(os.path.relpath(path, start=self.path), file)
                    for file in files if file.endswith('.kp')
                )

        for post in sorted([post[2:] if post.startswith('./') else post for post in posts]):
            yield post

    # ------------- Post submission / addition user flow ----------------------
    def _add_prepare(self, kp, path, update=False, **kwargs):
        pass

    def _add_cleanup(self, kp, path, update=False, **kwargs):
        pass

    def _submit(self, path=None, branch=None, force=False):
        pass  # Added posts are already submitted

    def _publish(self, path):  # Publish a post for general perusal
        pass  # Added posts are already published

    def _unpublish(self, path):  # unpublish a post for general perusal
        raise NotImplementedError

    def _accept(self, path):  # Approve to publish a post for general perusal
        pass

    def _remove(self, path, all=False):
        shutil.rmtree(os.path.join(self.path, path))

    # ------------ Knowledge Post Data Retrieval Methods -------------------------

    def _kp_uuid(self, path):
        try:
            return self._kp_read_ref(path, 'UUID')
        except:
            return None

    def _kp_path(self, path, rel=None):
        return KnowledgeRepository._kp_path(self, os.path.expanduser(path), rel=rel or self.path)

    def _kp_exists(self, path, revision=None):
        return os.path.exists(os.path.join(self.path, path))

    def _kp_status(self, path, revision=None, detailed=False, branch=None):
        return self.PostStatus.PUBLISHED

    def _kp_get_revision(self, path):
        # We use a 'REVISION' file in the knowledge post folder rather than using git
        # revisions because using git rev-parse is slow.
        try:
            return int(self._kp_read_ref(path, 'REVISION'))
        except:
            return 0

    def _kp_get_revisions(self, path):
        raise NotImplementedError

    def _kp_write_ref(self, path, reference, data, uuid=None, revision=None):
        path = os.path.join(self.path, path)
        if os.path.isfile(path):
            kp = KnowledgePost.from_file(path, format='kp')
            kp._write_ref(reference, data)
            kp.to_file(path, format='kp')
        else:
            ref_path = os.path.join(path, reference)
            ref_dir = os.path.dirname(ref_path)
            if not os.path.exists(ref_dir):
                os.makedirs(ref_dir)
            with open(ref_path, 'wb') as f:
                return f.write(data)

    def _kp_dir(self, path, parent=None, revision=None):  # TODO: Account for revision
        path = os.path.join(self.path, path)
        if os.path.isdir(path):
            if parent:
                path = os.path.join(path, parent)
            for dirpath, dirnames, filenames in os.walk(os.path.join(self.path, path)):
                for filename in filenames:
                    if dirpath == "" and filename == "REVISION":
                        continue
                    yield os.path.relpath(os.path.join(dirpath, filename), os.path.join(self.path, path))
        else:
            kp = KnowledgePost.from_file(path, format='kp')
            for reference in kp._dir(parent=parent):
                yield reference

    def _kp_has_ref(self, path, reference, revision=None):  # TODO: Account for revision
        path = os.path.join(self.path, path)
        if os.path.isdir(path):
            return os.path.isfile(os.path.join(path, reference))
        else:
            kp = KnowledgePost.from_file(path, format='kp')
            return kp._has_ref(reference)

    def _kp_diff(self, path, head, base):
        raise NotImplementedError

    def _kp_new_revision(self, path, uuid=None):
        self._kp_write_ref(path, "REVISION", encode(self._kp_get_revision(path) + 1))
        if uuid:
            self._kp_write_ref(path, "UUID", encode(uuid))

    def _kp_read_ref(self, path, reference, revision=None):
        path = os.path.join(self.path, path)
        if os.path.isdir(path):
            with open(os.path.join(self.path, path, reference), 'rb') as f:
                return f.read()
        else:
            kp = KnowledgePost.from_file(path, format='kp')
            return kp._read_ref(reference)
