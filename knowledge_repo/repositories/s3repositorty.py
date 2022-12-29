import os
from ..repository import KnowledgeRepository
from ..utils.files import get_path
import logging

logger = logging.getLogger(__name__)


class S3Repository(KnowledgeRepository):
    _registry_keys = ['s3', 's3a', 'gs', 'gcs']

#   https://s3.us-west-2.amazonaws.com/www.knowledge-repo.com/example/example_ipynb.kp/knowledge.md

    TEMPLATES = {
        'README.md': get_path(
            __file__, '../templates', 'repository_readme.md'),
        '.knowledge_repo_config.yml': get_path(
            __file__, '../templates', 'repository_config.yml'),
    }

    def init(self, config='.knowledge_repo_config.yml', auto_create=False):
        self.auto_create = auto_create
        self.path = self.uri
        self.config.update(os.path.join(self.path, config))

    @property
    def path(self):
        """
        Cloud storage path is the abstraction of ULR for various Cloud Storage
        Engine such as AWS S3 and GCP GCS
        """
        return self._path

    @path.setter
    def path(self, path):
        assert isinstance(path, str), 'The path specified must be a string.'
        path = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(path):
            path = os.path.abspath(path)
            if self.auto_create:
                self.create(path)
            else:
                raise ValueError(f"Provided path '{path}' does not exist.")
        self._path = path