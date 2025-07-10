from fastapi import UploadFile, File, HTTPException, APIRouter, Depends
from uuid import uuid4
from sqlalchemy.orm import Session
import os
from src.tasks_module.file_task import parse_and_process_resume, upload_file_to_s3, process_candidate_video
from src.services.file_services import persist_candidate_info
from fastapi import Form
from src.db_util.util import get_db
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg", ".tiff"}
UPLOAD_DIR = "uploads"  # make sure this path exists or is configurable



@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    job_id: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

        file_bytes = await file.read()
        s3_key = upload_file_to_s3(file_bytes, ext)
        candidate_info = parse_and_process_resume(s3_key)
        if candidate_info:
            candidate_info["session_id"] = "db743770-2a84-4faf-91b6-ffb45d5064f8"
            candidate_info["job_id"] = job_id
            print("##@@###candidte info",candidate_info )
        return {
            "status": "Uploaded to S3 and processing triggered",
            "s3_key": "s3_key",
            "session_id": session_id,
            "job_id": job_id,
        }

    except Exception as e:
        import logging
        logging.exception("Resume upload failed")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.post("/upload_video/")
async def upload_video(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    job_id: str = Form(...),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported video format")

    file_bytes = await file.read()

    # Upload video to S3
    s3_key = await upload_file_to_s3(file_bytes, file.filename)

    process_candidate_video(session_id, job_id, s3_key)

    return {
        "status": "Video uploaded and processing started",
        "s3_key": s3_key,
        "session_id": session_id,
        "job_id": job_id,
    }
