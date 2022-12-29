from ..repository import KnowledgeRepository
from ..utils.files import get_path
import logging

logger = logging.getLogger(__name__)


class CloudStorageRepository(KnowledgeRepository):
    _registry_keys = ['s3', 's3a', 'gs', 'gcs']

    TEMPLATES = {
        'README.md': get_path(
            __file__, '../templates', 'repository_readme.md'),
        '.knowledge_repo_config.yml': get_path(
            __file__, '../templates', 'repository_config.yml'),
    }

    # [TODO] 
    def init(self, auto_create=True):
        return True

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
                logger.warning(f"Not overriding existing file '{filename}'.")
        return FolderKnowledgeRepository(path)