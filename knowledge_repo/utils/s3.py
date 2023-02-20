from botocore.exceptions import ClientError
import boto3
import logging
import os
import json
import re

logger = logging.getLogger(__name__)
AWS_S3_AUTH_PATH = '.configs/aws_s3_auth.json'


def parse_s3_uri(s3_uri):
    """Get s3_path for S3 Object URL

    :param s3_url: url of s3 object
    :return: s3_bucket, s3_client
    """

    matches = re.match("s3://(.*?)/(.*)/(.*)/", s3_uri)
    if matches:
        bucket, _, key_name = matches.groups()
    else:
        raise ValueError(f'Cannot interpret {s3_uri}')
    return bucket, get_s3_client(), key_name


def get_s3_client():
    """Get a boto3 client for S3 operations

    :param s3_aws_access_key_id: aws access key id for s3
    :param s3_aws_secret_access_key: aws secret access key for s3
    :param s3_region_name: aws region name for s3
    :return: a boto3 client for s3 operations
    """

    with open(AWS_S3_AUTH_PATH) as source:
        credentials_dict = json.load(source)

    return boto3.client(
        "s3",
        aws_access_key_id=credentials_dict["S3_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=credentials_dict["S3_AWS_SECRET_ACCESS_KEY"],
        region_name=credentials_dict["S3_AWS_REGION_NAME"],
    )


def upload_file_to_s3(
    s3_client,
    file_name,
    bucket,
    object_name=None,
    content_type="binary/octet-stream",
):
    """Upload a file to an object in an S3 bucket

    :param s3_client: a boto3 S3 client
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified, file_name is used
    :param content_type: AWS S3 Content Type, default to "binary/octet-stream"
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
            ExtraArgs={'ContentType': content_type}
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


# TODO handle post remove and update
def download_dir_from_s3(
    s3_client,
    s3_bucket,
    s3_prefix,
    local_dir='tmp_kp'
):
    """Download a file from an object in an S3 bucket

    :param s3_client: a boto3 S3 client
    :param s3_bucket: Bucket to download from
    :param s3_prefix: pattern to match in s3 objects, can be treated as dir
    :param local_dir: local s3 path
    :return: list of kp post locationls
    """
    keys = []
    dirs = []
    next_token = ''
    base_kwargs = {
        'Bucket': s3_bucket,
        'Prefix': s3_prefix,
    }
    while next_token is not None:
        kwargs = base_kwargs.copy()
        if next_token != '':
            kwargs.update({'ContinuationToken': next_token})
        results = s3_client.list_objects_v2(**kwargs)
        if results.get('Contents') is None:
            return
        for i in results.get('Contents'):
            key = i.get('Key')
            if key[-1] != '/':
                keys.append(key)
            else:
                dirs.append(key)
        next_token = results.get('NextContinuationToken')
    # create dir in case empty path in S3
    for dir in dirs:
        dest_pathname = os.path.join(local_dir, dir)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
    # copy files from S3
    for object_key in keys:
        dest_pathname = os.path.join(local_dir, object_key)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
        logger.info("Down files from: {object_key} to {dest_pathname}".format(
            object_key=object_key,
            dest_pathname=dest_pathname)
        )
        s3_client.download_file(s3_bucket, object_key, dest_pathname)
    return dirs


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
