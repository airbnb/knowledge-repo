from __future__ import print_function

import cooked_input as ci
import logging
import os
import re
import time

import webbrowser

from .docx import DocxConverter

logger = logging.getLogger(__name__)


class GDocConverter(DocxConverter):
    _registry_keys = ['gdoc']

    def _find_doc(self, path, after=None, max_attempts=60, delay=1):
        """
        Look in the nominated path for a new "docx" document for a file modified
        after `after`. If none are found, retry every `delay` seconds for at
        most `max_attempts` attempts. If no documents are found, raise a
        `RuntimeError`.
        """
        count = 0
        while count < max_attempts:
            count += 1
            if count == 10:
                logger.info(
                    "So far unable to find a new 'docx' file in %s. If you "
                    "downloaded the Google Document elsewhere, please move it "
                    "into this folder.",
                    path
                )
            if not os.path.exists(path):
                break
            for filename in os.listdir(path):
                if filename.endswith('.docx'):
                    fpath = os.path.join(path, filename)
                    if os.path.getmtime(fpath) > after:
                        return fpath
            time.sleep(delay)

        if self.interactive:
            fpath = ci.get_string(
                prompt=(
                    "We were unable to find the downloaded Google Doc in the "
                    "expected path: '{}'. If the document was downloaded "
                    "elsewhere, please enter the full path of downloaded "
                    "document now (including file name)"
                    .format(path)
                ),
                required=False
            )
            if fpath:
                return fpath
        raise RuntimeError("Cannot find 'docx' document in {}.".format(path))

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
        logger.info("Looking for downloaded Google Docs file in '{}'...".format(download_path))
        filename = self._find_doc(download_path, after=time_start)

        DocxConverter.from_file(self, filename, **opts)

        headers = self.kp.headers
        if 'title' in headers and headers['title'].startswith('[]'):
            headers['title'] = re.sub(r'\[\]\{[^\}]+\}', '', headers['title'])
        if 'subtitle' in headers and headers['subtitle'].startswith('[]'):
            headers['subtitle'] = re.sub(r'\[\]\{[^\}]+\}', '', headers['subtitle'])
        self.kp.update_headers(**headers)
