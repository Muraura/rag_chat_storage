from uuid import uuid4
from datetime import datetime
from src.utils import mysql_query_utils, validation_util
from src.db_util.models import CandidateInfo, ChatSession
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request, HTTPException, status
from src.db_util.util import get_db
from fastapi.responses import JSONResponse

async def persist_candidate_info(db, candidate_info_dict):
    # session_id = candidate_info_dict.get("session_id")
    session_id ="db743770-2a84-4faf-91b6-ffb45d5064f8"
    if not session_id:
        return JSONResponse(content={"detail": "Missing session_id"}, status_code=400)

    # Check if candidate already exists for this session
    existing_candidate_id = await mysql_query_utils.get_field_details(
        db=db,
        query_model=CandidateInfo,
        query_object={"session_id": session_id},
        get_field="id"
    )

    candidate_data = {
        "name": candidate_info_dict.get("name"),
        "email": candidate_info_dict.get("email"),
        "phone": candidate_info_dict.get("phone"),
        "skills": candidate_info_dict.get("skills"),
        "education": candidate_info_dict.get("education"),
        "latest_company": candidate_info_dict.get("latest_company"),
        "location": candidate_info_dict.get("location"),
        "similarity_score": candidate_info_dict.get("similarity_score"),
        "raw_text_snippet": candidate_info_dict.get("raw_text_snippet"),
        "source_path": candidate_info_dict.get("source_path"),
        "session_id": session_id,
        "created_at": datetime.utcnow(),
    }

    if not existing_candidate_id:
        candidate_data["id"] = str(uuid4())
        await mysql_query_utils.create_field_details(db, CandidateInfo, candidate_data)
        return {"detail": "Candidate info saved", "candidate_id": candidate_data["id"]}
    else:
        candidate_data["updated_at"] = datetime.utcnow()
        await mysql_query_utils.update_field_details(
            db,
            CandidateInfo,
            query_object={"session_id": session_id},
            update_object=candidate_data
        )
        return {"detail": "Candidate info updated", "candidate_id": existing_candidate_id}


