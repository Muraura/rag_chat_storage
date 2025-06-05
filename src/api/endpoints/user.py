from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import uuid4

from src.utils import mysql_query_utils, validation_util
from src.db_util.models import User
from src.db_util.util import get_db
from src.auth.api_auth import get_api_key
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", dependencies=[Depends(get_api_key)])
async def create_user(payload: dict, db: Session = Depends(get_db)):
    print("nmmnnnnn")
    validation_list = [
        {"field": "email", "alias": "Email"}
    ]

    messages = validation_util.field_validation(payload, validation_list)
    if messages:
        return JSONResponse(content={"detail": messages}, status_code=400)
    print("ffndjddjj")
    try:
        payload["id"] = str(uuid4())

        await mysql_query_utils.create_field_details(db, User, payload)
        logger.info("#user.py #create_user #User created successfully")
        return {"detail": "User created successfully", "user_id": payload["id"]}

    except Exception as e:
        logger.error("#user.py #create_user #Exception: {}".format(e), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")
