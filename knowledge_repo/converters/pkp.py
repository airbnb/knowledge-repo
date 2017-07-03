import zipfile
import io

from nbconvert.exporters.exporter import Exporter

from ..converter import KnowledgePostConverter


class IpynbFormat(KnowledgePostConverter):
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
        zf = zipfile.ZipFile(filename, 'r')

        for ref in zf.namelist():
            with zf.open(ref) as f:
                self.kp._write_ref(ref, f.read())

        zf.close()

     #   raise RuntimeError("Portable Knowledge Post is invalid!")


class NBConvertExporter(Exporter):

    def from_notebook_node(self, nb, resources=None, **kw):
        """
        Convert a notebook from a notebook node instance.
        Parameters
        ----------
        nb : :class:`~nbformat.NotebookNode`
          Notebook node (dict-like with attr-access)
        resources : dict
          Additional resources that can be accessed read/write by
          preprocessors and filters.
        `**kw`
          Ignored
        """
        nb_copy = copy.deepcopy(nb)
        resources = self._init_resources(resources)

        if 'language' in nb['metadata']:
            resources['language'] = nb['metadata']['language'].lower()

        # Preprocess
        nb_copy, resources = self._preprocess(nb_copy, resources)

        return nb_copy, resources
