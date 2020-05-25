from __future__ import absolute_import
from builtins import next
from builtins import object
from collections import namedtuple
import io
import itertools
import os
import posixpath
import re
import collections
import logging
import datetime
import yaml
import base64
import uuid

import cooked_input as ci
import PIL.Image
import six

from .utils.encoding import encode, decode

logger = logging.getLogger(__name__)

# Define available headers, their types, and runtime input specification
Header = namedtuple('Header', ('name', 'type', 'input'))

HEADER_REQUIRED_FIELD_TYPES = [
    Header('title', six.string_types, ci.GetInput(prompt='title')),
    Header('authors', list, ci.GetInput(prompt='authors (comma separated)', convertor=ci.ListConvertor())),
    Header('tldr', six.string_types, ci.GetInput(prompt='tldr')),
    Header('created_at', datetime.datetime, ci.GetInput(prompt='created_at', convertor=ci.DateConvertor(), default=datetime.date.today())),
]

HEADER_OPTIONAL_FIELD_TYPES = [
    Header('subtitle', six.string_types, ci.GetInput(prompt='subtitle', required=False)),
    Header('tags', list, ci.GetInput(prompt='tags (comma separated)', convertor=ci.ListConvertor(), required=False)),
    Header('path', six.string_types, ci.GetInput(prompt='path', required=False)),
    Header('updated_at', datetime.datetime, ci.GetInput(prompt='updated_at', convertor=ci.DateConvertor(), default=datetime.datetime.now())),
    Header('private', bool, ci.GetInput(prompt='private', convertor=ci.BooleanConvertor(), required=False)),   # If true, this post starts out private
    Header('allowed_groups', list, ci.GetInput(prompt='allowed_groups (comma separated)', convertor=ci.ListConvertor(), required=False)),
    Header('thumbnail', (int, ) + six.string_types, ci.GetInput(prompt='thumbnail', required=False)),
]

HEADERS_ALL = {
    header.name: header
    for header in itertools.chain(HEADER_REQUIRED_FIELD_TYPES, HEADER_OPTIONAL_FIELD_TYPES)
}

# Headers to prompt for if missing when in interactive mode
HEADERS_INTERACTIVE = ['title', 'subtitle', 'authors', 'tldr', 'created_at', 'tags']


HEADER_SAMPLE = """
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
thumbnail: 2
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

    yaml.SafeDumper.add_representer(collections.OrderedDict, dict_representer)
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
                    yield posixpath.join(key, path)
            else:
                yield key


class KnowledgePost(object):
    '''
    A "Knowledge Post" is a (virtual) folder in which there is a 'knowledge.md' file,
    and potentially an 'images' and/or 'src' folder. It is "virtual" in the sense
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
            if self.__cache[posixpath.join(parent or '', ref)] is not None:
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
            mtch = re.match('^---\n[\\s\\S]+?---\n', md)
            if not mtch:
                raise ValueError("YAML header is missing. Please ensure that the top of your post has a header of the following form:\n" + HEADER_SAMPLE)
            if not headers:
                md = re.sub('^---\n[\\s\\S]+?---\n', '', md, count=1)
            if not body:
                md = mtch.group(0)
        if images:
            return md, self.read_images()
        return md

    @property
    def image_paths(self):
        return ['images/{}'.format(image_name) for image_name in self._dir(parent='images')]

    def read_image(self, name):
        return self._read_ref('images/' + name)

    def read_images(self):
        image_data = {}
        for image_path in self.image_paths:
            image_data[image_path] = self._read_ref(image_path)
        return image_data

    @property
    def src_paths(self):
        srcs = ['src/{}'.format(src_name) for src_name in self._dir(parent='src')]
        legacy_srcs = ['orig_src/{}'.format(src_name) for src_name in self._dir(parent='orig_src')]  # TODO: deprecate
        return srcs + legacy_srcs

    def read_src(self, ref):
        # Read src reference, first attempting to read from `src`, then from
        # the legacy `orig_src`, path.
        try:
            return self._read_ref('src/' + ref)
        except Exception as e:
            if self._has_ref('orig_src/' + ref):
                return self._read_ref('orig_src/' + ref)
            raise e

    def write(self, md, headers=None, images={}, interactive=False):
        md = md.strip()

        if not headers:
            headers = self._get_headers_from_yaml(md)

        md = re.sub(r'^---\n[\s\S]+?---\n', '', md, count=1)

        headers = self._verify_headers(headers, interactive=interactive)

        md = (  # Format with unicode seems to have issue in Python 2, so we explicitly concatenate
            '---\n' +
            yaml.safe_dump(headers, default_flow_style=False) +
            '---\n\n' +
            md
        )

        self._write_ref('knowledge.md', encode(md))

        for image, data in list(images.items()):
            self._write_ref('images/' + image, data)

    def write_image(self, name, data):
        self._write_ref('images/' + name, data)

    def write_images(self, image_data={}):
        for name, data in list(self.image_data.items()):
            self.write_image(name, data)

    def write_src(self, name, data):
        self._write_ref('src/' + name, encode(data))

    def add_srcfile(self, filename, name=None):
        if not name:
            name = os.path.basename(filename)
        with open(filename, 'rb') as f:
            self.write_src(name, f.read())

    # ------------- Knowledge Post Format ----------------------------------

    def _get_headers_from_yaml(self, yaml_str):
        try:
            if not yaml_str.strip().startswith('---'):
                raise StopIteration()
            return next(yaml.load_all(yaml_str))
        except yaml.YAMLError as e:
            logger.info(
                "YAML header is incorrectly formatted or missing. The following "
                "information may be useful:\n{}\nIf you continue to have "
                "difficulties, try pasting your YAML header into an online parser "
                "such as http://yaml-online-parser.appspot.com/.".format(str(e))
            )
        except StopIteration as e:
            logger.info('YAML header is missing!')
        return {}

    def _verify_headers(self, headers, interactive=False):
        if not isinstance(headers, dict):
            raise RuntimeError()
        missing_required_headers = (
            set(h.name for h in HEADER_REQUIRED_FIELD_TYPES).difference(headers)
        )

        if interactive:
            missing_suggested_headers = (
                set(HEADERS_INTERACTIVE).difference(headers).difference(missing_required_headers)
            )

            if missing_required_headers:
                print("This post is missing the following required headers: {}".format(missing_required_headers))
            if missing_suggested_headers:
                print("This post is missing the following suggested headers: {}".format(missing_suggested_headers))
            if missing_required_headers or missing_suggested_headers:
                print(
                    "You will now be prompted for each missing header. If you wish "
                    "to abort the knowledge post creation, press Ctrl+C."
                    .format(missing_required_headers)
                )

                for header in HEADERS_INTERACTIVE:
                    if header not in headers:
                        headers[header] = HEADERS_ALL[header].input.get_input()
        elif missing_required_headers:
            raise RuntimeError(
                "Knowledge post is missing required headers {}. Please rerun this "
                "operation in interactive mode, or add headers manually to the "
                "post source file.".format(missing_required_headers)
            )

        for key, value in list(headers.items()):
            if value is None:
                del headers[key]

        if 'tags' not in headers or not headers['tags']:
            headers['tags'] = []
        headers['updated_at'] = datetime.datetime.now()

        return headers

    @property
    def headers(self):
        headers = self._get_headers_from_yaml(self.read(body=False))
        if not headers:
            raise ValueError("YAML header is missing. Please ensure that the top of your post has a header of the following form:\n" + HEADER_SAMPLE)
        for key, value in headers.copy().items():
            if isinstance(value, datetime.date):
                headers[key] = datetime.datetime.combine(value, datetime.time(0))
            if key == 'tags' and isinstance(value, list):
                headers[key] = [str(v) if six.PY3 else unicode(v) for v in value]
        return headers

    @headers.setter
    def headers(self, headers):
        self.write(self.read(headers=False), headers=headers)

    def update_headers(self, **headers):
        h = self.headers
        for header, value in headers.items():
            if value is None:
                if header in h:
                    h.pop(header)
            else:
                h[header] = value
        self.headers = h

    @property
    def thumbnail_uri(self):
        thumbnail = self.headers.get('thumbnail')

        if not thumbnail or not isinstance(thumbnail, six.string_types):
            return None

        if ':' not in thumbnail:  # if thumbnail points to a local reference
            if not self._has_ref(thumbnail):
                return None

            data_in = io.BytesIO(self._read_ref(thumbnail))
            data_out = io.BytesIO()

            try:  # Attempt to generate 125x125 png thumbnail from resource
                im = PIL.Image.open(data_in)

                # 125x125 is approximately the maximum size we can guarantee
                # will fit in the thumbnail uri data field, with max characters
                # of 65535 for a PNG with 32 bits per pixel
                im.thumbnail((125, 125))

                data_out = io.BytesIO()
                im.save(data_out, 'png')
                data_out.seek(0)
                thumbnail_data = data_out.read()

                data = base64.b64encode(thumbnail_data)
                thumbnail = (
                    'data:{};base64,'.format('image/png') +
                    data.decode('utf-8')
                )
            except Exception as e:
                logger.warning(
                    "Thumbnail generation failed for {}: {}."
                    .format(self.path, e)
                )
                return None
            finally:
                data_in.close()
                data_out.close()

        return thumbnail

    def is_valid(self):
        if not self._has_ref('knowledge.md'):
            return False
        try:
            FormatChecks().process(self)
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
    def from_file(cls, filename, src_paths=[], format=None, postprocessors=None, interactive=False, **opts):
        kp = KnowledgePostConverter.for_file(cls(), filename, format=format, postprocessors=postprocessors, interactive=interactive).from_file(filename, **opts)
        if src_paths:
            for src_path in src_paths:
                kp.add_srcfile(src_path)
        return kp

    @classmethod
    def from_string(cls, string, src_strings={}, format=None, postprocessors=None, interactive=False, **opts):
        kp = KnowledgePostConverter.for_format(cls(), format=format, postprocessors=postprocessors, interactive=interactive).from_string(string, ** opts)
        if src_strings:
            for src_name, data in list(src_strings.items()):
                kp.write_src(src_name, data)
        return kp

    def to_file(self, filename, format=None, interactive=False, **opts):
        return KnowledgePostConverter.for_file(self, filename, format=format, interactive=interactive).to_file(filename, **opts)

    def to_string(self, format, interactive=False, **opts):
        return KnowledgePostConverter.for_format(self, format, interactive=interactive).to_string(**opts)


from .converter import KnowledgePostConverter  # noqa
from .postprocessors.format_checks import FormatChecks  # noqa
from .postprocessors.extract_images import ExtractImages  # noqa
