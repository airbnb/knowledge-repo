from __future__ import absolute_import
from builtins import next
from builtins import object
import os
import posixpath
import re
import collections
import logging
import datetime
import yaml
import mimetypes
import base64
import uuid

from .utils.encoding import encode, decode

logger = logging.getLogger(__name__)


SAMPLE_HEADER = """
---
title: "This is a Knowledge Post title, quoted so we can use special characters like ':'"
authors:
- sally_smarts
- wesly_wisdom
tags:
- knowledge
- example
created_at: 2016-06-29
updated_at: 2016-06-30
tldr: |
    You can write any markdown you want here (the '|' character makes this an escaped section)

    * bullet
    * bullet

    You can even write arbitrary html (html is valid markdown)
    <table>
    <tr>
    <th>hi</th>
    <th>I'm </th>
    </tr>
    <tr>
    <td>a</td>
    <td>table</td>
    </tr>
    </table>
---
"""


# Use OrderedDict representations in Yaml, so post headers remain in order
# Although this sets it for all uses of yaml in this Python instance,
# this shouldn't cause any problems.
def setup_yaml():
    _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

    def dict_representer(dumper, data):
        return dumper.represent_dict(data.items())

    def dict_constructor(loader, node):
        return collections.OrderedDict(loader.construct_pairs(node))

    yaml.add_representer(collections.OrderedDict, dict_representer)
    yaml.add_constructor(_mapping_tag, dict_constructor)


setup_yaml()


class ReferenceCache(object):

    def __init__(self, cache=None):
        self._cache = cache or {}

    def __setitem__(self, key, value):
        parents = posixpath.dirname(key).split('/')
        cache = self._cache
        for parent in parents:
            if parent:
                if parent not in cache:
                    cache[parent] = {}
                cache = cache[parent]
        cache[posixpath.basename(key)] = value

    def __getitem__(self, key):
        parents = posixpath.dirname(key).split('/')
        cache = self._cache
        for parent in parents:
            if parent:
                cache = cache[parent]
        return cache[posixpath.basename(key)]

    def __delitem__(self, key):
        parents = posixpath.dirname(key).split('/')
        cache = self._cache
        for parent in parents:
            if parent:
                cache = cache[parent]
        del cache[posixpath.basename(key)]

    def __getattr__(self, key):
        if key not in self._cache:
            raise AttributeError
        if isinstance(self._cache[key], dict):
            return ReferenceCache(self._cache[key])
        return self._cache[key]

    def keys(self):
        return list(self._cache.keys())

    def get(self, key, default=None):
        try:
            return self[key]
        except:
            return default

    def __contains__(self, key):
        try:
            parents = posixpath.dirname(key).split('/')
            cache = self._cache
            for parent in parents:
                if parent:
                    cache = cache[parent]
            return posixpath.basename(key) in cache
        except KeyError:
            return False

    def dir(self, parent=None, cache=None):
        if cache is None:
            cache = self._cache
            if parent:
                cache = cache.get(parent, {})
        for key in cache:
            if isinstance(cache[key], dict):
                for path in self.dir(parent=posixpath.join(parent or '', key), cache=cache[key]):
                    yield path
            else:
                yield posixpath.join(parent or '', key)


class KnowledgePost(object):
    '''
    A "Knowledge Post" is a (virtual) folder in which there is a 'knowledge.md' file,
    and potentially an 'images' and/or 'orig_src' folder. It is "virtual" in the sense
    that `KnowledgePost` objects store everything in memory, and use `KnowledgeRepository`
    object instances to interface with "physical" realisations of them. For example,
    in a GitKnowledgeRepository, the physical realisation is an actual folder; whereas
    in a database-backed KnowledgeRepository, on the virtual structure is maintained.
    '''

    def __init__(self, path=None, revision=None, repository=None):
        self.path = path
        self.revision = revision
        self.repository = repository
        self.__cache = ReferenceCache()  # Mapping of string filename to data

    @property
    def repository_uri(self):
        if (self.repository is not None):
            return self.repository._kp_repository_uri(self.path)

    @property
    def path(self):
        return self._path or self.headers.get('path')

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def uuid(self):
        if not getattr(self, '_uuid', None):
            if self.repository is not None:
                self._uuid = self.repository._kp_uuid(self.path)  # Use repository UUID (even if None)
            else:
                self._uuid = str(uuid.uuid4())
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):
        self._uuid = uuid

    # ------------ Reference cache methods ------------------------------------------
    def _read_ref(self, ref):
        if (ref not in self.__cache) and (self.repository is not None) and self.repository._kp_has_ref(self.path, ref):
            self.__cache[ref] = self.repository._kp_read_ref(self.path, ref)
        return self.__cache[ref]

    def _write_ref(self, ref, data):
        self.__cache[ref] = data

    def _drop_ref(self, ref):
        del self.__cache[ref]

    def _has_ref(self, ref):
        return (ref in self.__cache) or (self.repository is not None) and self.repository._kp_has_ref(self.path, ref)

    def _dir(self, parent=None):
        for ref in self.__cache.dir(parent=parent):
            if self.__cache[ref] is not None:
                yield ref
        if self.repository is not None:
            for ref in self.repository._kp_dir(self.path, parent=parent, revision=self.revision):
                if ref not in self.__cache:
                    yield ref

    # ---------- Knowledge Post Data Population -----------------------------

    def read(self, images=False, headers=True, body=True):
        if not (body or headers):
            md = ''
        else:
            md = decode(self._read_ref('knowledge.md'))
            mtch = re.match('^---\n[\s\S]+?---\n', md)
            if not mtch:
                raise ValueError("YAML header is missing. Please ensure that the top of your post has a header of the following form:\n" + SAMPLE_HEADER)
            if not headers:
                md = re.sub('^---\n[\s\S]+?---\n', '', md, count=1)
            if not body:
                md = mtch.group(0)
        if images:
            return md, self.read_images()
        return md

    @property
    def image_paths(self):
        return ['images/{}'.format(image_name) for image_name in self._dir(parent='images')]

    def read_image(self, name):
        return self._read_ref('image/' + name)

    def read_images(self):
        image_data = {}
        for image_path in self.image_paths:
            image_data[image_path] = self._read_ref(image_path)
        return image_data

    def read_src(self, ref):
        return self._read_ref('orig_src/' + ref)

    def write(self, md, headers=None, images={}):
        md = md.strip()
        if headers is not None:
            md = re.sub('^---\n[\s\S]+?---\n', '', md, count=1)
            md = '---\n' + \
                yaml.dump(headers, default_flow_style=False) + '---\n' + md
        md += '\n'

        self._write_ref('knowledge.md', encode(md))

        for image, data in list(images.items()):
            self._write_ref('images/' + image, data)

    def write_image(self, name, data):
        self._write_ref('images/' + name, data)

    def write_images(self, image_data={}):
        for name, data in list(self.image_data.items()):
            self.write_image(name, data)

    def write_src(self, name, data):
        self._write_ref('orig_src/' + name, encode(data))

    def add_srcfile(self, filename, name=None):
        if not name:
            name = os.path.basename(filename)
        with open(filename, 'rb') as f:
            self.write_src(name, f.read())

    # ------------- Knowledge Post Format ----------------------------------

    @property
    def headers(self):
        try:
            headers = next(yaml.load_all(self.read(body=False)))
        except StopIteration as e:
            raise ValueError("YAML header is missing. Please ensure that the top of your post has a header of the following form:\n" + SAMPLE_HEADER)
        except yaml.YAMLError as e:
            raise ValueError(
                "YAML header is incorrectly formatted or missing. The following information may be useful:\n{}\nIf you continue to have difficulties, try pasting your YAML header into an online parser such as http://yaml-online-parser.appspot.com/.".format(str(e)))
        for key, value in headers.copy().items():
            if isinstance(value, datetime.date):
                headers[key] = datetime.datetime.combine(value, datetime.time(0))
        return headers

    def update_headers(self, **headers):
        h = self.headers
        h.update(headers)
        self.write(self.read(), headers=h)

    @property
    def thumbnail_uri(self):
        image_matches = ExtractImages.find_images(self.read())
        if len(image_matches) == 0:
            return None

        i = 0
        image_uri = None
        while not image_uri:
            if i == len(image_matches):
                return None
            image_uri = image_matches[i]['src']
            i += 1

        if ':' not in image_uri:  # TODO: Check this works
            if not os.path.exists(image_uri):
                return None
            with open(self.feed_image[7:]) as f:
                data = base64.b64encode(f.read())
            image_mimetype = mimetypes.guess_type(self.feed_image)[0]
            if image_mimetype is not None:
                return 'data:{};base64,'.format(image_mimetype) + data

        return image_uri

    def is_valid(self):
        if not self._has_ref('knowledge.md'):
            return False
        try:
            FormatChecks.process(self)
        except:
            return False
        return True

    @property
    def status(self):
        if self.repository is not None:
            return self.repository._kp_status(self.path, revision=self.revision)

    @property
    def is_published(self):
        return self.status == self.repository.PostStatus.PUBLISHED

    @property
    def is_accepted(self):
        return self.status in [self.repository.PostStatus.UNPUBLISHED, self.repository.PostStatus.PUBLISHED]

    @property
    def web_uri(self):
        if self.repository is not None:
            return self.repository._kp_web_uri(self.path)

    # Conversion/Import/Export methods
    @classmethod
    def from_file(cls, filename, src_paths=[], format=None, postprocessors=None, **opts):
        kp = KnowledgePostConverter.for_file(cls(), filename, format=format, postprocessors=postprocessors).from_file(filename, **opts)
        if src_paths:
            for src_path in src_paths:
                kp.add_srcfile(src_path)
        return kp

    @classmethod
    def from_string(cls, string, src_strings={}, format=None, postprocessors=None, **opts):
        kp = KnowledgePostConverter.for_format(cls(), format=format, postprocessors=postprocessors).from_string(string, ** opts)
        if src_strings:
            for src_name, data in list(src_strings.items()):
                kp.write_src(src_name, data)
        return kp

    def to_file(self, filename, format=None, **opts):
        return KnowledgePostConverter.for_file(self, filename, format=format).to_file(filename, **opts)

    def to_string(self, format, **opts):
        return KnowledgePostConverter.for_format(self, format).to_string(**opts)

from .converter import KnowledgePostConverter  # noqa
from .postprocessors.format_checks import FormatChecks  # noqa
from .postprocessors.extract_images import ExtractImages  # noqa
