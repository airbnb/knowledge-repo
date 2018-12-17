import os
import posixpath
import re
import six
import logging

from ..postprocessor import KnowledgePostProcessor

logger = logging.getLogger(__name__)


class ExtractImages(KnowledgePostProcessor):
    _registry_keys = ['extract_images']

    def process(self, kp):
        images = self.find_images(kp.read())
        image_mapping = self.collect_images(kp, images)
        self.update_thumbnail_uri(kp, images, image_mapping)
        self.cleanup(kp)

    def update_thumbnail_uri(self, kp, images, image_mapping):
        thumbnail = kp.headers.get('thumbnail', 0)

        # if thumbnail is a number, select the nth image in this post as the thumbnail
        if isinstance(thumbnail, six.string_types) and thumbnail.isdigit():
            thumbnail = int(thumbnail)
        if isinstance(thumbnail, int):
            if len(images) > 0:
                image_index = 0
                if thumbnail < len(images):
                    image_index = thumbnail
                thumbnail = images[image_index]['src']
            else:
                thumbnail = None

        # if thumbnail is a url, copy it locally to the post unless already collected during collection
        if thumbnail and not self.skip_image(kp, {'src': thumbnail}):
            orig_path = os.path.join(kp.orig_context, os.path.expanduser(thumbnail))
            if thumbnail in image_mapping:
                thumbnail = image_mapping[thumbnail]
            elif os.path.exists(orig_path):
                thumbnail = self.copy_image(kp, orig_path)
            else:
                logger.warning("Could not find a thumbnail image at: {}".format(thumbnail))

        # update post headers to point to new thumbnail image
        kp.update_headers(thumbnail=thumbnail)

    def find_images(self, md):
        images = []
        images.extend(self.collect_images_for_pattern(
            md,
            # Match all <img /> tags with attributes of form <name>(="<value>") with optional quotes (can be single or double)
            # The src attribute is exected to always be surrounded by quotes.
            r'<img\s+(?:\w+(?:=([\'\"])?(?(1)(?:(?!\1).)*?\1|[^>]*?))?\s+?)*src=([\'\"])(?P<src>(?:(?!\2).)*?)\2(?:\s+\w+(?:=([\'\"])?(?(1)(?:(?!\4).)*?\4|[^>]*?))?)*\s*\/?>'
        ))
        images.extend(self.collect_images_for_pattern(md, r'\!\[[\s\S]*?\]\((?P<src>[^\)]*)\)'))
        return sorted(images, key=lambda x: x['offset'])

    def collect_images_for_pattern(self, md, pattern=None):
        p = re.compile(pattern)
        return [{'offset': m.start(), 'tag': m.group(0), 'src': m.group('src')} for m in p.finditer(md)]

    def collect_images(self, kp, images):
        image_mapping = {}
        if len(images) == 0:
            return image_mapping
        md = kp.read()
        images = images[::-1]
        for image in images:
            if self.skip_image(kp, image):
                continue
            orig_path = os.path.join(kp.orig_context, os.path.expanduser(image['src']))
            new_path = None
            if image['src'] in image_mapping:
                new_path = image_mapping[image['src']]
            elif kp._has_ref(image['src']):
                new_path = self.copy_image(kp, image['src'], is_ref=True)
            elif os.path.exists(orig_path):
                new_path = self.copy_image(kp, orig_path)
            else:
                logger.warning("Could not find an image at: {}".format(image['src']))
            if not new_path:
                continue
            image_mapping[image['src']] = new_path
            md = self.replace_image_locations(md, image['offset'], image['tag'], image['src'], new_path)
        kp.write(md)
        return image_mapping

    def skip_image(self, kp, image):
        if re.match('http[s]?://', image['src']):
            return True
        if image['src'].startswith('images/') and image['src'] in kp.image_paths:
            return True
        return False

    def copy_image(self, kp, path, is_ref=False):
        if is_ref:
            return
        with open(path, 'rb') as f:
            kp.write_image(os.path.basename(path), f.read())
        return posixpath.join('images', os.path.basename(path))

    def replace_image_locations(self, md, offset, match, old_path, new_path):
        pre = md[:offset]
        post = md[offset + len(match):]
        return pre + match.replace(old_path, new_path) + post

    def cleanup(self, kp):
        pass
