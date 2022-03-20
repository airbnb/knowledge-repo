from ..constants import MD
from ..converter import KnowledgePostConverter
from knowledge_repo.utils.files import read_text


class MdConverter(KnowledgePostConverter):
    _registry_keys = [MD]

    def from_file(self, filename):
        self.kp_write(read_text(filename))
