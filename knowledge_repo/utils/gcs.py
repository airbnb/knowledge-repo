from gcloud import storage
from gcloud.exceptions import GCloudError
from oauth2client.service_account import ServiceAccountCredentials
import os
import logging

logger = logging.getLogger(__name__)


def get_gcs_client(
    client_id,
    client_email,
    private_key_id,
    private_key,
    gc_project,
):
    credentials_dict = {
        'type': 'service_account',
        'client_id': client_id,
        'client_email': client_email,
        'private_key_id': private_key_id,
        'private_key': private_key,
    }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credentials_dict
    )
    return storage.Client(credentials=credentials, project=gc_project)


def upload_file_from_gcs(
    gcs_client,
    bucket,
    blob_name,
    file_name=None,
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
        response = blob.upload_from_filename(file_name)
        logger.info(response)
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
        blob.download_to_filename(local_dir + blob.name)
