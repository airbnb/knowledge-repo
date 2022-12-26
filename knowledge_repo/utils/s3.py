from botocore.exceptions import ClientError
import boto3
import logging
import os

logger = logging.getLogger(__name__)


def upload_file_to_s3(
    file_name,
    s3_aws_access_key_id,
    s3_aws_secret_access_key,
    s3_region_name,
    bucket,
    object_name=None,
):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param s3_aws_access_key_id: aws access key id for s3
    :param s3_aws_secret_access_key: aws secret access key for the above access key id
    :param s3_region_name: aws region name for s3
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=s3_aws_access_key_id,
        aws_secret_access_key=s3_aws_secret_access_key,
        region_name=s3_region_name,
    )
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        logger.info(response)
    except ClientError as client_error:
        logger.error(client_error)
        return False
    return True
