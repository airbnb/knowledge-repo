import os

from knowledge_repo.utils.s3 import parse_s3_uri, download_dir_from_s3
from ..repository import KnowledgeRepository
from ..utils.files import get_path
import logging

logger = logging.getLogger(__name__)


class S3Repository(KnowledgeRepository):
    _registry_keys = ['s3']

    TEMPLATES = {
        'README.md': get_path(
            __file__, '../templates', 'repository_readme.md'),
        '.knowledge_repo_config.yml': get_path(
            __file__, '../templates', 'repository_config.yml'),
    }

    def init(self, config='.knowledge_repo_config.yml', auto_create=False):
        self.auto_create = auto_create

        self._s3_bucket, self._s3_client, self._dir = parse_s3_uri(self.uri)
        self._path = os.path.join('tmp_kp', self._dir)
        download_dir_from_s3(self._s3_client, self._s3_bucket, self._dir, self._path)
        self.config.update(os.path.join(self.path, config))



    @classmethod
    def from_uri(cls, uri, *args, **kwargs):
        return cls(uri, *args, **kwargs)

    @property
    def path(self):
        """
        Cloud storage path is the abstraction of ULR for various Cloud Storage
        Engine such as AWS S3 and GCP GCS
        """
        return self._path

    @path.setter
    def path(self, path):
        self._path = path


    # ----------- Repository actions / state ----------------------------------
    @property
    def revision(self):
        pass


    @property
    def status(self):
        pass


    @property
    def status_message(self):
        pass

    # ---------------- Post retrieval methods --------------------------------

    def _dir(self, prefix, statuses):
        posts = set()

        if self.PostStatus.PUBLISHED in statuses:

            for path, folders, files in os.walk(os.path.join(self.path, prefix or "")):

                # Do not visit hidden folders
                for folder in folders:
                    if folder.startswith("."):
                        folders.remove(folder)

                posts.update(
                    os.path.join(os.path.relpath(path, start=self.path), folder)
                    for folder in folders
                    if folder.endswith(".kp")
                )
                posts.update(
                    os.path.join(os.path.relpath(path, start=self.path), file)
                    for file in files
                    if file.endswith(".kp")
                )

        for post in sorted(
            [post[2:] if post.startswith("./") else post for post in posts]
        ):
            yield post
        pass

    # ------------- Post submission / addition user flow ----------------------
    def _add_prepare(self, kp, path, update=False, **kwargs):
        pass

    def _add_cleanup(self, kp, path, update=False, **kwargs):
        pass

    def _submit(self, path=None, branch=None, force=False):
        pass

    def _publish(self, path):
        pass

    def _unpublish(self, path):
        raise NotImplementedError

    def _accept(self, path):
        pass

    def _remove(self, path, all=False):
        pass

    # ------------ Knowledge Post Data Retrieval Methods ----------------------

    def _kp_uuid(self, path):
        pass

    def _kp_path(self, path, rel=None):
        pass

    def _kp_exists(self, path, revision=None):
        pass

    def _kp_status(self, path, revision=None, detailed=False, branch=None):
        return self.PostStatus.PUBLISHED

    def _kp_get_revision(self, path):
        pass

    def _kp_get_revisions(self, path):
        raise NotImplementedError

    def _kp_write_ref(self, path, reference, data, uuid=None, revision=None):
        pass

    def _kp_dir(self, path, parent=None, revision=None):
        pass

    def _kp_has_ref(self, path, reference, revision=None):
        pass

    def _kp_diff(self, path, head, base):
        raise NotImplementedError

    def _kp_new_revision(self, path, uuid=None):
        pass

    def _kp_read_ref(self, path, reference, revision=None):
        pass
