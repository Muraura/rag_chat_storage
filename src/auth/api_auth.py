from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from src.core import server
from src.log_conf import Logger

LOGGER = Logger.get_logger(__name__)

# Define the expected header name
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)):
    expected_api_key = server.setting_config.get("ACCESS_TOKEN")

    LOGGER.info(f"🔐 Received API Key: {api_key}")
    LOGGER.info(f"🔐 Expected API Key: {expected_api_key}")

    if api_key == expected_api_key:
        return api_key
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
