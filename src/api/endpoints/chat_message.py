from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from datetime import datetime

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
        # Check if session exists
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
async def get_chat_messages(session_id: str, db: Session = Depends(get_db)):
    try:
        try:
            UUID(session_id)
        except ValueError:
            return JSONResponse(content={"detail": "Invalid session_id format"}, status_code=400)

        # Verify session exists
        session_exists = await mysql_query_utils.get_field_details(
            db, ChatSession, filters={"id": session_id}
        )
        if not session_exists:
            return JSONResponse(content={"detail": "Chat session not found"}, status_code=404)

        filters = {"session_id": session_id}
        messages = await mysql_query_utils.get_all_field_details(db, ChatMessage, filters)

        return {"messages": messages}
    except Exception as e:
        logger.error(f"#chat_message.py #get_chat_messages #Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get chat messages")


@router.delete("/{message_id}", dependencies=[Depends(get_api_key), Depends(limiter.limit("10/minute"))])
async def delete_chat_message(message_id: str, db: Session = Depends(get_db)):
    try:
        # Validate message_id format
        try:
            UUID(message_id)
        except ValueError:
            return JSONResponse(content={"detail": "Invalid message_id format"}, status_code=400)

        deleted = await mysql_query_utils.delete_field_details(
            db, ChatMessage, filters={"id": message_id}
        )
        if not deleted:
            return JSONResponse(content={"detail": "Message not found"}, status_code=404)

        logger.info(f"#chat_message.py #delete_chat_message #Deleted message {message_id}")
        return {"detail": "Message deleted successfully"}
    except Exception as e:
        logger.error(f"#chat_message.py #delete_chat_message #Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete chat message")
