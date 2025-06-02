import json
import os
import boto3
from botocore.exceptions import ClientError
from src.log_conf import Logger

LOGGER = Logger.get_logger(__name__)


class SecretsManagerClient:
    def __init__(self):
        try:
            self.client = boto3.client(
                'secretsmanager',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name='ap-south-1'
            )
        except ClientError as e:
            self.client = None
            LOGGER.error("Exception while connecting with Secrets Manager ----------> {}".format(str(e)))

    def get_secret(self, secret_name):
        try:
            get_secret_value_response = self.client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            LOGGER.error("Exception while fetching secret from Secrets Manager ----------> {}".format(str(e)))
            return None
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return json.loads(secret)
            else:
                LOGGER.error("Exception while fetching secret from Secrets Manager ----------> {}".format(str(e)))
                return None
