import os

from knowledge_repo.utils.s3 import parse_s3_uri, download_dir_from_s3, upload_file_to_s3
from ..post import KnowledgePost
from ..repository import KnowledgeRepository
from ..utils.files import get_path, read_binary, write_binary, remove_prefix
from ..utils.encoding import encode
import logging
import time

logger = logging.getLogger(__name__)


class S3Repository(KnowledgeRepository):
    _registry_keys = ['s3']
    _local_path = 'tmp_kp'

    TEMPLATES = {
        'README.md': get_path(
            __file__, '../templates', 'repository_readme.md'),
        '.knowledge_repo_config.yml': get_path(
            __file__, '../templates', 'repository_config.yml'),
    }

    def init(self, config='.knowledge_repo_config.yml', auto_create=False):
        self.auto_create = auto_create

        self._s3_bucket, self._s3_client, self._s3_dir = parse_s3_uri(self.uri)
        self._path = os.path.join(self._local_path, self._s3_dir)
        download_dir_from_s3(
            self._s3_client, self._s3_bucket, self._s3_dir, self._path)
        # self.config.update(os.path.join(self.path, config))

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
        return time.time()

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
                    os.path.join(os.path.relpath(
                        path, start=self.path), folder)
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

    # ------------- Post submission / addition user flow ----------------------
    def _save(self, file, file_path, src_paths=[]):
        kp = KnowledgePost.from_file(file, src_paths)
        self.add(kp, file_path)

        # upload files to S3
        for dirpath, dirnames, filenames in os.walk(os.path.join(self._path, file_path)):
            for filename in filenames:
                content_type = "text/html" if filename.endswith(".html") else "binary/octet-stream"
                upload_file_to_s3(self._s3_client, os.path.join(
                    dirpath, filename), self._s3_bucket, os.path.join(remove_prefix(dirpath, self._path), filename), content_type)

        # delete raw file after post processing and upload
        if os.path.exists(file):
            os.remove(file)

        # return knowledge post
        return kp

    def _add_prepare(self, kp, path, update=False, **kwargs):
        pass

    def _add_cleanup(self, kp, path, update=False, **kwargs):
        pass

    def _submit(self, path=None, branch=None, force=False):
        pass  # Added posts are already submitted

    def _publish(self, path):
        pass  # Added posts are already published

    def _unpublish(self, path):
        # Latest revision for published post
        revision = self._kp_get_revision(
            path, self.PostStatus.PUBLISHED, enforce_exists=True)
        self.__set_post_status(
            path, status=self.PostStatus.UNPUBLISHED, revision=revision)

    def _accept(self, path):
        pass

    def _remove(self, path, all=False):
        pass

    # ------------ Knowledge Post Data Retrieval Methods ----------------------

    def _kp_uuid(self, path):
        try:
            return self._kp_read_ref(path, "UUID")
        except Exception as ex:
            logger.info(f"Existing UUID file was not found.")
            return None

    def _kp_path(self, path, rel=None):
        return KnowledgeRepository._kp_path(
            self, os.path.expanduser(path), rel=rel or self.path
        )

    def _kp_exists(self, path, revision=None):
        return os.path.exists(os.path.join(self.path, path))

    def _kp_status(self, path, revision=None, detailed=False, branch=None):
        return self.PostStatus.PUBLISHED

    def _kp_get_revision(self, path):
        try:
            return int(self._kp_read_ref(path, "REVISION"))
        except Exception as e:
            print(f"Exception encountered: {e}")
            return 0

    def _kp_get_revisions(self, path):
        raise NotImplementedError

    def _kp_write_ref(self, path, reference, data, uuid=None, revision=None):
        ref_path = os.path.join(self.path, path, reference)
        ref_dir = os.path.dirname(ref_path)
        if not os.path.exists(ref_dir):
            os.makedirs(ref_dir)
        write_binary(ref_path, data)

    def _kp_dir(self, path, parent=None, revision=None):
        if os.path.isdir(os.path.join(self.path, path)):
            if parent:
                path = os.path.join(path, parent)
            for dirpath, dirnames, filenames in os.walk(os.path.join(self.path, path)):
                for filename in filenames:
                    if dirpath == "" and filename == "REVISION":
                        continue
                    yield os.path.relpath(
                        os.path.join(dirpath, filename), os.path.join(
                            self.path, path)
                    )
        else:
            kp = KnowledgePost.from_file(path, format="kp")
            for reference in kp._dir(parent=parent):
                yield reference

    def _kp_has_ref(self, path, reference, revision=None):
        path = os.path.join(self.path, path)
        if os.path.isdir(path):
            return os.path.isfile(os.path.join(path, reference))
        else:
            kp = KnowledgePost.from_file(path, format="kp")
            return kp._has_ref(reference)

    def _kp_diff(self, path, head, base):
        raise NotImplementedError

    def _kp_new_revision(self, path, uuid=None):
        self._kp_write_ref(path, "REVISION", encode(
            self._kp_get_revision(path) + 1))
        if uuid:
            self._kp_write_ref(path, "UUID", encode(uuid))

    def _kp_read_ref(self, path, reference, revision=None):
        path = os.path.join(self.path, path)
        if os.path.isdir(path):
            return read_binary(os.path.join(path, reference))
        else:
            kp = KnowledgePost.from_file(path, format="kp")
            return kp._read_ref(reference)
