from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import Query

import logging
logger = logging

from src.utils import mysql_query_utils, validation_util
from src.db_util.models import ChatMessage, ChatSession
from src.db_util.util import get_db
from src.auth.api_auth import get_api_key
from src.utils.rate_limiter import limiter

router = APIRouter()


@router.post("/")
@limiter.limit("20/minute")
async def add_chat_message(
    request: Request,
    payload: dict,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    validation_list = [
        {"field": "session_id", "alias": "Session ID"},
        {"field": "sender", "alias": "Sender"},
        {"field": "content", "alias": "Content"},
    ]

    messages = validation_util.field_validation(payload, validation_list)
    if messages:
        return JSONResponse(content={"detail": messages}, status_code=400)

    try:
        session_id = UUID(payload["session_id"])
    except ValueError:
        logger.warning("Invalid session_id format")
        return JSONResponse(content={"detail": "Invalid session_id format"}, status_code=400)

    try:
        session = await mysql_query_utils.get_field_details(
            db=db,
            query_model=ChatSession,
            query_object={"id": str(session_id)},
            get_field="id"
        )
        if not session:
            return JSONResponse(content={"detail": "Chat session not found"}, status_code=404)

        message_data = {
            "id": str(uuid4()),
            "session_id": str(session_id),
            "sender": payload["sender"],
            "content": payload["content"],
            "context": payload.get("context"),
            "created_at": datetime.utcnow(),
        }

        await mysql_query_utils.create_field_details(db, ChatMessage, message_data)

        logger.info(f"Message added successfully for session_id={session_id}")
        return {"detail": "Message added successfully", "message_id": message_data["id"]}

    except Exception as e:
        logger.error(f"Exception in add_chat_message: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add chat message")


@router.get("/session/{session_id}", dependencies=[Depends(get_api_key)])
@limiter.limit("20/minute")
async def get_chat_messages(
    request: Request,
    session_id: str,
    limit: int = Query(20, gt=0, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    try:
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            logger.warning(f"Invalid session_id format: {session_id}")
            return JSONResponse(content={"detail": "Invalid session_id format"}, status_code=400)
        session_exists = await mysql_query_utils.get_field_details(
            db=db,
            query_model=ChatSession,
            query_object={"id": str(session_uuid)},
            get_field="id"
        )
        if not session_exists:
            logger.info(f"Chat session not found for session_id={session_id}")
            return JSONResponse(content={"detail": "Chat session not found"}, status_code=404)
        query = db.query(ChatMessage).filter_by(session_id=str(session_uuid))
        total = query.count()
        messages = query.order_by(ChatMessage.created_at).offset(offset).limit(limit).all()

        logger.info(f"Fetched {len(messages)} messages for session_id={session_id}")
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "messages": jsonable_encoder(messages)
        }

    except Exception as e:
        logger.error(f"Exception in get_chat_messages: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get chat messages")


@router.delete(
    "/{message_id}",
    dependencies=[Depends(get_api_key)],
)
@limiter.limit("10/minute")
async def delete_chat_message(
    request: Request,
    message_id: str,
    db: Session = Depends(get_db)
):
    try:
        try:
            UUID(message_id)
        except ValueError:
            logger.warning(f"Invalid message_id format: {message_id}")
            return JSONResponse(content={"detail": "Invalid message_id format"}, status_code=400)
        deleted = mysql_query_utils.delete_field_details(
            db=db,
            model=ChatMessage,
            filters={"id": message_id}
        )

        if not deleted:
            logger.info(f"Message not found for deletion: {message_id}")
            return JSONResponse(content={"detail": "Message not found"}, status_code=404)

        logger.info(f"Message deleted successfully: {message_id}")
        return {"detail": "Message deleted successfully"}

    except Exception as e:
        logger.error(f"Exception in delete_chat_message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete chat message")

