from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from fastapi.responses import JSONResponse

import logging
logger = logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from uuid import uuid4
from datetime import datetime
from src.utils import mysql_query_utils, validation_util
from src.db_util.models import ChatSession, User
from src.db_util.util import get_db
from src.auth.api_auth import get_api_key
from src.utils.rate_limiter import limiter
from slowapi.errors import RateLimitExceeded
from fastapi.exception_handlers import request_validation_exception_handler


router = APIRouter()


@router.post("/")
@limiter.limit("10/minute")
async def create_chat_session(request: Request, payload: dict, db: Session = Depends(get_db)):
    validation_list = [
        {"field": "user_id", "alias": "User ID"},
        {"field": "name", "alias": "Session Name"}
    ]
    messages = validation_util.field_validation(payload, validation_list)
    if messages:
        return JSONResponse(content={"detail": messages}, status_code=400)

    try:
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        payload["id"] = str(uuid4())
        payload["created_at"] = datetime.utcnow()
        payload["updated_at"] = datetime.utcnow()
        await mysql_query_utils.create_field_details(db, ChatSession, payload)
        logger.info("#chat.py #create_chat_session #Session created successfully")
        return {"detail": "Chat session created successfully", "session_id": payload["id"]}

    except Exception as e:
        logger.error(f"#chat.py #create_chat_session #Exception: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )


@router.patch("/{session_id}")
@limiter.limit("10/minute")
async def update_chat_session(
    request: Request,
    session_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    if not payload:
        return JSONResponse(content={"detail": "Empty payload"}, status_code=400)

    allowed_fields = {"name", "is_favorite"}
    disallowed = [key for key in payload if key not in allowed_fields]

    if disallowed:
        return JSONResponse(
            content={"detail": f"Invalid fields in payload: {disallowed}"},
            status_code=400
        )

    try:
        payload["updated_at"] = datetime.utcnow()
        updated = await mysql_query_utils.update_field_details(
            db,
            ChatSession,
            query_object={"id": session_id},
            update_object=payload
        )

        if not updated:
            return JSONResponse(content={"detail": "Session not found"}, status_code=404)

        logger.info(f"#chat_sessions.py #update_chat_session #Updated session {session_id}")
        return {"detail": "Chat session updated successfully"}

    except Exception as e:
        logger.error(f"#chat_sessions.py #update_chat_session #Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update chat session")


@router.delete("/{session_id}")
@limiter.limit("10/minute")
async def delete_chat_session(
    request: Request,
    session_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    try:
        deleted = await mysql_query_utils.delete_field_details(
            db, ChatSession, filters={"id": session_id}
        )

        if not deleted:
            return JSONResponse(content={"detail": "Session not found"}, status_code=404)

        logger.info(f"#chat_sessions.py #delete_chat_session #Deleted session {session_id}")
        return {"detail": "Chat session deleted successfully"}

    except Exception as e:
        logger.error(f"#chat_sessions.py #delete_chat_session #Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete chat session")


@router.get("/")
async def list_chat_sessions(
    request: Request,
    user_id: str = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    try:
        filters = {"user_id": user_id} if user_id else {}
        sessions = await mysql_query_utils.get_all_field_details(db, ChatSession, filters)

        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"#chat_sessions.py #list_chat_sessions #Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list chat sessions")
