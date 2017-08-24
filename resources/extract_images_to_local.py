import os
import posixpath
import random
import string
import logging
import time
import tempfile
from knowledge_repo.postprocessors.extract_images import ExtractImages

logger = logging.getLogger(__name__)

LOCAL_HTTP_SERVER_ROOT = 'http://localhost:8000'
LOCAL_HTTP_SERVER_DIRECTORY = 'static-server'


class ExtractImagesToLocalServer(ExtractImages):
    _registry_keys = ['extract_images_to_local']

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
            random_string = ''.join(
                random.choice(string.ascii_lowercase) for i in range(6))
            fname_img = '{repo_name}_{time}_{random_string}{ext}'.format(
                repo_name=repo_name,
                time=int(round(time.time() * 100)),
                random_string=random_string,
                ext=img_ext).strip().replace(' ', '-')

            # See if a static file directory exists, if not, let's create
            if not os.path.exists(LOCAL_HTTP_SERVER_DIRECTORY):
                os.makedirs(LOCAL_HTTP_SERVER_DIRECTORY)
            # Copy images to local http server directory
            cmd = "cp {} {}/{}".format(
                tmp_path, LOCAL_HTTP_SERVER_DIRECTORY, fname_img)
            logger.info("Copying image {} to {}/{}".format(
                tmp_path, LOCAL_HTTP_SERVER_DIRECTORY, fname_img))
            retval = os.system(cmd)
            if retval != 0:
                raise Exception('Problem copying images')
        finally:
            # Clean up temporary file
            if is_ref:
                os.remove(tmp_path)

        # return uploaded path of file
        return posixpath.join(LOCAL_HTTP_SERVER_ROOT, fname_img)

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
