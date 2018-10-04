import os
import re
import sys
import time

import webbrowser

import knowledge_repo
import subprocess

from .docx import DocxConverter


class GDocConverter(DocxConverter):
    _registry_keys = ['gdoc']

    def _find_doc(self, path, after=None):
        count = 0
        while count < 60:
            count += 1
            for filename in os.listdir(path):
                if filename.endswith('.docx'):
                    fpath = os.path.join(path, filename)
                    if os.path.getmtime(fpath) > after:
                        return fpath
            time.sleep(1)
        raise RuntimeError("Cannot find document.")

    def from_file(self, url, download_path=None, **opts):
        m = re.match('https://docs.google.com/document/d/(?P<doc_id>[^/]+)/', url)

        if not m:
            raise ValueError("Invalid Google Docs url.")

        doc_id = m.group('doc_id')
        download_url = "https://docs.google.com/document/d/{doc_id}/export?format=doc".format(doc_id=doc_id)

        time_start = time.time()
        webbrowser.open(download_url)

        time.sleep(2)

        download_path = download_path or os.path.expanduser('~/Downloads')
        filename = self._find_doc(download_path, after=time_start)

        DocxConverter.from_file(self, filename, **opts)

        headers = self.kp.headers
        if headers['title'].startswith('[]'):
            headers['title'] = re.sub('\[\]\{[^\}]+\}', '', headers['title'])
        if headers['subtitle'].startswith('[]'):
            headers['subtitle'] = re.sub('\[\]\{[^\}]+\}', '', headers['subtitle'])
        self.kp.update_headers(**headers)
