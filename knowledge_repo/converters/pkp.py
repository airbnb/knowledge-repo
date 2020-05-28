import zipfile
import io
import os

from ..converter import KnowledgePostConverter


class PkpConverter(KnowledgePostConverter):
    _registry_keys = ['kp', 'zip']

    def to_file(self, filename):
        zf = zipfile.ZipFile(filename, 'w')

        for ref in self.kp._dir():
            zf.writestr(ref, self.kp._read_ref(ref))

        zf.close()

    def to_string(self):
        data = io.BytesIO()
        zf = zipfile.ZipFile(data, 'w')

        for ref in self.kp._dir():
            zf.writestr(ref, self.kp._read_ref(ref))

        zf.close()
        data.seek(0)
        return data.read()

    def from_file(self, filename):
        # Note: header checks are not applied here, since it should not be
        # possible to create portable knowledge post with incorrect headers.
        zf = zipfile.ZipFile(filename, 'r')

        for ref in zf.namelist():
            with zf.open(ref) as f:
                self.kp._write_ref(ref, f.read())

        zf.close()
