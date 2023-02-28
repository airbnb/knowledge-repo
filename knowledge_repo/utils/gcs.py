from gcloud import storage
from gcloud.exceptions import GCloudError
from oauth2client.service_account import ServiceAccountCredentials
import os
import logging
import re
import json

logger = logging.getLogger(__name__)
GOOGLE_AUTH_PATH = '.configs/google_auth.json'


def parse_gcs_uri(uri):
    """Get google cloud storage path from uri

    :param uri: "gs://(.*?)/(.*)"
    :return: bucket and path
    """
    matches = re.match("gs://(.*?)/(.*)", uri)
    if matches:
        return matches.groups()
    else:
        raise ValueError(f'Cannot interpret {uri}')


def get_gcs_client():

    with open(GOOGLE_AUTH_PATH) as source:
        credentials_dict = json.load(source)

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credentials_dict
    )
    return storage.Client(credentials=credentials, project=credentials_dict['project_id'])


def upload_file_to_gcs(
    gcs_client,
    file_name,
    bucket,
    blob_name,
):
    """Upload a file from an object in an GCS
    :param gcs_client: a gcloud client
    :param bucket: Bucket to upload from
    :param blob_name: blob name
    :param file_name: File to upload. If not specified, blob_name is used
    :return: True if file was uploaded, else False
    """

    # If file_name was not specified, use object_name
    if file_name is None:
        file_name = os.path.basename(blob_name)

    # Upload the file
    try:
        bucket = gcs_client.get_bucket(bucket)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_name)
        logger.info("knowledge_repo uploaded successfully")
    except GCloudError as client_error:
        logger.error(client_error)
        return False
    return True


def download_file_from_gcs(
    gcs_client,
    bucket,
    blob_name,
    file_name=None,
):
    """Download a file from an object in an GCS
    :param gcs_client: a gcloud client
    :param bucket: Bucket to download from
    :param blob_name: blob name
    :param file_name: File to download. If not specified, blob_name is used
    :return: True if file was downloaded, else False
    """

    # If file_name was not specified, use object_name
    if file_name is None:
        file_name = os.path.basename(blob_name)

    # Download the file
    try:
        bucket = gcs_client.get_bucket(bucket)
        blob = bucket.blob(blob_name)
        response = blob.download_to_filename(file_name)
        logger.info(response)
    except GCloudError as client_error:
        logger.error(client_error)
        return False
    return True


# TODO handle post remove and update
def download_dir_from_gcs(
    gcs_client,
    bucket,
    blob_prefix,
    local_dir='tmp_kp',
):
    """Download a file from an object in an GCS
    :param gcs_client: a gcloud client
    :param bucket: Bucket to download from
    :param blob_prefix: Blob name prefix
    :param local_dif: Local directory to download.
    :return: True if file was downloaded, else False
    """

    gc_bucket = gcs_client.get_bucket(bucket_name=bucket)
    blobs = gc_bucket.list_blobs(prefix=blob_prefix)  # Get list of files
    for blob in blobs:
        if not blob.name.endswith('/'):
            dest_pathname = os.path.join(local_dir + blob.name)
            if not os.path.exists(os.path.dirname(dest_pathname)):
                os.makedirs(os.path.dirname(dest_pathname))
            logger.info("Down files from: {object_key} to {dest_pathname}".format(
                object_key=blob.name,
                dest_pathname=dest_pathname)
            )
            blob.download_to_filename(local_dir + blob.name)
