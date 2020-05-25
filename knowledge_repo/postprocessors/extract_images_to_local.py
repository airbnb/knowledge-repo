import os
import shutil
import random
import string
import logging
import time
import tempfile

try:
    from urllib.parse import urljoin
except ImportError:  # Python 2
    from urlparse import urljoin

from .extract_images import ExtractImages


logger = logging.getLogger(__name__)


class ExtractImagesToLocalServer(ExtractImages):
    """
    This KnowledgePostProcessor subclass extracts images from posts to a local
    directory. It is assumed that a local http server is then serving these images
    from the local directory. It is designed to be used upon addition to a knowledge
    repository, which can reduce the size of repositories. It replaces local images
    with urls relative to `http_image_root` (the base url of the local http server).

    `image_dir` should be the root of the image folder which is accessible locally.
    `http_image_root` should be the root of the server where the images will be
    accessible (e.g. 'http://localhost:8000').
    """

    _registry_keys = ['extract_images_to_local']

    def __init__(self, image_dir, http_image_root):
        self.image_dir = image_dir
        self.http_image_root = http_image_root

    def copy_image(self, kp, img_path, is_ref=False, repo_name='knowledge'):
        # Copy image data to new file
        if is_ref:
            _, tmp_path = tempfile.mkstemp()
            with open(tmp_path, 'wb') as f:
                f.write(kp._read_ref(img_path))
        else:
            tmp_path = img_path

        try:
            # Get image type
            img_ext = os.path.splitext(img_path)[1]

            # Make random filename for image
            random_string = ''.join(
                random.choice(string.ascii_lowercase) for i in range(6))
            fname_img = '{repo_name}_{time}_{random_string}{ext}'.format(
                repo_name=repo_name,
                time=int(round(time.time() * 100)),
                random_string=random_string,
                ext=img_ext).strip().replace(' ', '-')

            # See if a static file directory exists, if not, let's create
            if not os.path.exists(self.image_dir):
                os.makedirs(self.image_dir)

            # Copy images to local http server directory
            new_path = os.path.join(self.image_dir, fname_img)
            logger.info("Copying image {} to {}".format(tmp_path, new_path))
            try:
                shutil.copyfile(tmp_path, new_path)
            except Exception as e:
                raise Exception('Problem copying image: {}'.format(e))

        finally:
            # Clean up temporary file
            if is_ref:
                os.remove(tmp_path)

        # return uploaded path of file
        return urljoin(self.http_image_root, fname_img)

    def skip_image(self, kp, image):
        import re
        if re.match('http[s]?://', image['src']):
            return True
        return False

    def cleanup(self, kp):
        if kp._has_ref('images'):
            kp._drop_ref('images')
