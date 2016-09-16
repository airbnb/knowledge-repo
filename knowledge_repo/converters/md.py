from ..converter import KnowledgePostConverter


class MdConverter(KnowledgePostConverter):
    _registry_keys = ['md']

    def from_file(self, filename):
        with open(filename) as f:
            self.kp.write(f.read())
