import os
import re
import logging

from ..postprocessor import KnowledgePostProcessor

logger = logging.getLogger(__name__)


class ExtractImages(KnowledgePostProcessor):
    _registry_keys = ['extract_images']

    @classmethod
    def process(cls, kp):
        images = cls.find_images(kp.read())
        image_mapping = cls.collect_images(kp, images)
        cls.update_thumbnail_uri(kp, images, image_mapping)
        cls.cleanup(kp)

    @classmethod
    def update_thumbnail_uri(cls, kp, images, image_mapping):
        thumbnail = kp.headers.get('thumbnail', 0)

        # if thumbnail is a number, select the nth image in this post as the thumbnail
        if isinstance(thumbnail, str) and thumbnail.isdigit():
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
        if thumbnail and not cls.skip_image(kp, {'src': thumbnail}):
            orig_path = os.path.join(kp.orig_context, os.path.expanduser(thumbnail))
            if thumbnail in image_mapping:
                thumbnail = image_mapping[thumbnail]
            elif os.path.exists(orig_path):
                thumbnail = cls.copy_image(kp, orig_path)
            else:
                logger.warning("Could not find a thumbnail image at: {}".format(thumbnail))

        # update post headers to point to new thumbnail image
        kp.update_headers(thumbnail=thumbnail)

    @classmethod
    def find_images(cls, md):
        images = []
        images.extend(cls.collect_images_for_pattern(
            md,
            # Match all <img /> tags with attributes of form <name>(="<value>") with optional quotes (can be single or double)
            # The src attribute is exected to always be surrounded by quotes.
            r'<img\s+(?:\w+(?:=([\'\"])?(?(1)(?:(?!\1).)*?\1|[^>]*?))?\s+?)*src=([\'\"])(?P<src>(?:(?!\2).)*?)\2(?:\s+\w+(?:=([\'\"])?(?(1)(?:(?!\4).)*?\4|[^>]*?))?)*\s*\/?>'
        ))
        images.extend(cls.collect_images_for_pattern(md, r'\!\[.*\]\((?P<src>[^\)]*)\)'))
        return sorted(images, key=lambda x: x['offset'])

    @classmethod
    def collect_images_for_pattern(cls, md, pattern=None):
        p = re.compile(pattern)
        return [{'offset': m.start(), 'tag': m.group(0), 'src': m.group('src')} for m in p.finditer(md)]

    @classmethod
    def collect_images(cls, kp, images):
        image_mapping = {}
        if len(images) == 0:
            return image_mapping
        md = kp.read()
        images = images[::-1]
        for image in images:
            if cls.skip_image(kp, image):
                continue
            orig_path = os.path.join(kp.orig_context, os.path.expanduser(image['src']))
            new_path = None
            if image['src'] in image_mapping:
                new_path = image_mapping[image['src']]
            elif kp._has_ref(image['src']):
                new_path = cls.copy_image(kp, image['src'], is_ref=True)
            elif os.path.exists(orig_path):
                new_path = cls.copy_image(kp, orig_path)
            else:
                logger.warning("Could not find an image at: {}".format(image['src']))
            if not new_path:
                continue
            image_mapping[image['src']] = new_path
            md = cls.replace_image_locations(md, image['offset'], image['tag'], image['src'], new_path)
        kp.write(md)
        return image_mapping

    @classmethod
    def skip_image(cls, kp, image):
        if re.match('http[s]?://', image['src']):
            return True
        if image['src'].startswith('images/') and image['src'] in kp.image_paths:
            return True
        return False

    @classmethod
    def copy_image(cls, kp, path, is_ref=False):
        if is_ref:
            return
        with open(path, 'rb') as f:
            kp.write_image(os.path.basename(path), f.read())
        return os.path.join('images', os.path.basename(path))

    @classmethod
    def replace_image_locations(cls, md, offset, match, old_path, new_path):
        pre = md[:offset]
        post = md[offset + len(match):]
        return pre + match.replace(old_path, new_path) + post

    @classmethod
    def cleanup(cls, kp):
        pass
