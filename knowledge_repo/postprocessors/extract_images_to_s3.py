import os
import posixpath
import random
import string
import logging
import tempfile
import time

from .extract_images import ExtractImages


logger = logging.getLogger(__name__)


class ExtractImagesToS3(ExtractImages):
    '''
    This KnowledgePostProcessor subclass extracts images from posts to S3. It
    is designed to be used upon addition to a knowledge repository, which can
    reduce the size of repositories. It replaces local images with remote urls
    based on `http_image_root`.

    `s3_image_root` should be the root of the image folder on an S3 remote, such
    as "s3://my_bucket/images".
    `http_image_root` should be the root of the server where the images will be
    accessible after uploading.

    Note: This requires that user AWS credentials are set up appropriately and
    that they have installed the aws cli packages.
    '''
    _registry_keys = ['extract_images_to_s3']

    def __init__(self, s3_image_root, http_image_root):
        self.s3_image_root = s3_image_root
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
            img_ext = posixpath.splitext(img_path)[1]

            # Make random filename for image
            random_string = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
            fname_img = '{repo_name}_{time}_{random_string}{ext}'.format(
                repo_name=repo_name,
                time=int(round(time.time() * 100)),
                random_string=random_string,
                ext=img_ext).strip().replace(' ', '-')

            # Copy image to accessible folder on S3
            fname_s3 = posixpath.join(self.s3_image_root, repo_name, fname_img)
            # Note: The following command may need to be prefixed with a login agent;
            # for example, to handle multi-factor authentication.
            cmd = "aws s3 cp '{0}' {1}".format(tmp_path, fname_s3)
            logger.info("Uploading images to S3: {cmd}".format(cmd=cmd))
            retval = os.system(cmd)
            if retval != 0:
                raise Exception('Problem uploading images to s3')
        finally:
            # Clean up temporary file
            if is_ref:
                os.remove(tmp_path)

        # return uploaded path of file
        return posixpath.join(self.http_image_root, repo_name, fname_img)

    def skip_image(self, kp, image):
        import re
        if re.match('http[s]?://', image['src']):
            return True
        return False

    def cleanup(self, kp):
        if kp._has_ref('images'):
            kp._drop_ref('images')
