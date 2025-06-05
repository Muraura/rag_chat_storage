"""
fastapi settings for config project.

"""
import json
import os
from typing import List
import boto3
from pydantic import BaseSettings
from src.log_conf import Logger

LOGGER = Logger.get_logger(__name__)


def load_s3_config():
    environment = os.environ.get('ENVIRONMENT')
    if environment == "PRODUCTION":
        key = "integration-service/prod.json"
    else:
        key = "integration-service/local.json"
    access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    try:
        client = boto3.client('s3',
                              aws_access_key_id=access_key_id,
                              aws_secret_access_key=secret_access_key
                              )

        config_data = client.get_object(Bucket="appsecretcreds", Key=key)
        config_data = json.loads(config_data['Body'].read().decode())
        return config_data
    except Exception as e:
        LOGGER.error("Exception while fetching configuration file from S3 bucket ----------> {}".format(str(e)))


class LocalAPISettings(BaseSettings):
    api_v1_route: str = "/integration-service/api/v1"
    openapi_route: str = "/integration-service/api/v1/openapi.json"

    backend_cors_origins_str: str = "*"  # Should be a comma-separated list of origins

    server_address: str = "0.0.0.0"
    server_port: int = 8082
    server_log_level: str = "debug"
    debug: bool = False
    debug_exceptions: bool = False
    disable_superuser_dependency: bool = False
    include_admin_routes: bool = False
    config_data = load_s3_config()
    LOGGER.info("Config variables integration-microservice app : {}".format(str(config_data)))
    LOGGER.info("Config variables integration-microservice app : {}".format(type(config_data)))

    @property
    def backend_cors_origins(self) -> List[str]:
        return [x.strip() for x in self.backend_cors_origins_str.split(",") if x]

    class Config:
        env_prefix = ""


class ProdAPISettings(BaseSettings):
    api_v1_route: str = "/integration-service/api/v1"
    openapi_route: str = "/integration-service/api/v1/openapi.json"

    backend_cors_origins_str: str = "*"

    server_address: str = "0.0.0.0"
    server_port: int = 8082
    server_log_level: str = "debug"
    debug: bool = False
    debug_exceptions: bool = False
    disable_superuser_dependency: bool = False
    include_admin_routes: bool = False
    config_data = load_s3_config()
    print("FJFKFKJFconfig_data", config_data)

    @property
    def backend_cors_origins(self) -> List[str]:
        return [x.strip() for x in self.backend_cors_origins_str.split(",") if x]

    class Config:
        env_prefix = ""


class FactoryConfig:
    """Returns a config instance depending on the ENV_STATE variable."""

    def __init__(self, env_state: str):
        self.env_state = env_state

    def __call__(self):
        return ProdAPISettings()
