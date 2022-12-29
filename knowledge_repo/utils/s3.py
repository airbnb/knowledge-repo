from botocore.exceptions import ClientError
import boto3
import logging
import os
from s3path import S3Path

logger = logging.getLogger(__name__)


def parse_s3_path(s3_url):
    """Get s3_path for S3 Object URL

    :param s3_url: url of s3 object
    :return: bucket and key name
    """
    path = S3Path.from_uri(s3_url)
    return path.bucket, path.key


def get_s3_client(
    s3_aws_access_key_id,
    s3_aws_secret_access_key,
    s3_region_name,
):
    """Get a boto3 client for S3 operations

    :param s3_aws_access_key_id: aws access key id for s3
    :param s3_aws_secret_access_key: aws secret access key for s3
    :param s3_region_name: aws region name for s3
    :return: a boto3 client for s3 operations
    """

    return boto3.client(
        "s3",
        aws_access_key_id=s3_aws_access_key_id,
        aws_secret_access_key=s3_aws_secret_access_key,
        region_name=s3_region_name,
    )


def upload_file_to_s3(
    s3_client,
    file_name,
    bucket,
    object_name=None,
):
    """Upload a file to an object in an S3 bucket

    :param s3_client: a boto3 S3 client
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified, file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name.replace("\\", "/"))

    # Upload the file
    try:
        response = s3_client.upload_file(
            file_name,
            bucket,
            object_name,
        )
        logger.info(response)
    except ClientError as client_error:
        logger.error(client_error)
        return False
    return True


def download_file_from_s3(
    s3_client,
    bucket,
    object_name,
    file_name=None,
):
    """Download a file from an object in an S3 bucket

    :param s3_client: a boto3 S3 client
    :param bucket: Bucket to download from
    :param object_name: S3 object name
    :param file_name: File to download. If not specified, object_name is used
    :return: True if file was downloaded, else False
    """

    # If file_name was not specified, use object_name
    if file_name is None:
        file_name = os.path.basename(object_name)

    # Download the file
    try:
        response = s3_client.download_file(bucket, object_name, file_name)
        logger.info(response)
    except ClientError as client_error:
        logger.error(client_error)
        return False
    return True


def put_object_to_s3(
    s3_client,
    data,
    bucket,
    object_name,
    content_type="binary/octet-stream",
):
    """Put object data in an S3 bucket

    :param s3_client: a boto3 S3 client
    :param data: data to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified, file_name is used
    :param content_type: AWS S3 Content Type, default to "binary/octet-stream"
    :return: True if file was uploaded, else False
    """

    # Put Object
    try:
        response = s3_client.put_object(
            Body=data,
            Bucket=bucket,
            Key=object_name,
            CacheControl="no-cache",
            ContentType=content_type,
        )
        logger.info(response)
    except ClientError as client_error:
        logger.error(client_error)
        return False
    return True
