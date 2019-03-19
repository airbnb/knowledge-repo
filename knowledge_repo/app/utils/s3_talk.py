"""
Given S3 path download to local and trigger upload to database repository
"""
import os
import boto3,botocore
import tempfile
import errno

BUCKET_NAME = os.environ['KR_BUCKET_NAME']
S3 = boto3.resource('s3')
CLIENT = boto3.client('s3')

def assert_dir(path):
    """
    Checks if directory tree in path exists.     :param path: the path to check if it exists
    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def _extract_name(path):
# Internal function to return name of the folder/file to use downstream
    if path.endswith('/'):
        return path.split('/')[-2]
    else:
        return path.split('/')[-1]

def download_dir(path):
    """
    Downloads recursively the given S3 path to the target directory.
    arg path: The S3 directory to download.
    """

    # Handle missing / at end of prefix
    if not path.endswith('/'):
        path += '/'

    dir_name = _extract_name(path)
    target = "/tmp/%s/"%dir_name

    paginator = CLIENT.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=BUCKET_NAME, Prefix=path):
        # Download each file individually
        for key in result['Contents']:
            # Calculate relative path
            rel_path = key['Key'][len(path):]
            # Skip paths ending in /
            if not key['Key'].endswith('/'):
                local_file_path =  os.path.join(target, rel_path)
                # Make sure directories exist
                local_file_dir = os.path.dirname(local_file_path)
                assert_dir(local_file_dir)
                CLIENT.download_file(BUCKET_NAME, key['Key'], local_file_path)
    return dir_name,target




def download_from_s3(path):
    try: 
        fname = _extract_path(path)
        temp_name = '/tmp/%s'%fname
        S3.Bucket(BUCKET_NAME).download_file(path,temp_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return -1

    return fname,temp_name
