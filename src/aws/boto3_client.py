import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from src.log_conf import Logger
import json

LOGGER = Logger.get_logger(__name__)

access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')


def create_boto3_client():
    """Generate a boto3 cleint to use the s3 servces

        :params: no parameters are required
        :return: boto3 client as object. If error, returns None.
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=Config(signature_version='s3v4', region_name='ap-south-1')
        )
    except ClientError as e:
        LOGGER.error("Exception while connecting with S3 bucket ----------> {}".format(str(e)))
        return None

    return s3_client


def read_from_s3_bucket(bucket_name, file_name, file_type):
    """Reads a json file from s3 bucket

        :params: bucket_name: name of the bucket
        :params: file_name: name of the file to be read
        :return: json data. If error, returns None.
    """
    s3_client = create_boto3_client()
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        data = response['Body'].read().decode('utf-8')
        if file_type == 'json':
            return json.loads(data)
        else:
            return data
    except ClientError as e:
        LOGGER.error("Exception while reading file from S3 bucket ----------> {}".format(str(e)))
        return None
