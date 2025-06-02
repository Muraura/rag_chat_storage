from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from src.core import server
from src.log_conf import Logger

LOGGER = Logger.get_logger(__name__)

API_KEY_NAME = "access-token"
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
):
    api_key = server.setting_config.get("ACCESS_TOKEN")

    if api_key_query == api_key:
        return api_key_query
    elif api_key_header == api_key:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
