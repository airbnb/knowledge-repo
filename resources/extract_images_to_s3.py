import os
import posixpath
import random
import string
import logging
import time
import tempfile
from knowledge_repo.postprocessors.extract_images import ExtractImages

logger = logging.getLogger(__name__)

S3_IMAGE_ROOT = 's3://<aws images folder>'
HTTP_IMAGE_ROOT = 'http://<url where images are exposed>'


class ExtractImagesToS3(ExtractImages):
    '''
    Use this to bootstrap your own KnowledgePostprocessor.
    '''
    _registry_keys = ['extract_images_to_s3']

    @classmethod
    def copy_image(cls, kp, img_path, is_ref=False, repo_name='knowledge'):
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
            fname_s3 = posixpath.join(S3_IMAGE_ROOT, repo_name, fname_img)
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
        return posixpath.join(HTTP_IMAGE_ROOT, repo_name, fname_img)

    @classmethod
    def skip_image(cls, kp, image):
        import re
        if re.match('http[s]?://', image['src']):
            return True
        return False

    @classmethod
    def cleanup(cls, kp):
        if kp._has_ref('images'):
            kp._drop_ref('images')
