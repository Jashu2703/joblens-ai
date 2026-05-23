import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.resume import Resume
from app.utils.resume_parser import parse_resume

router = APIRouter()

ALLOWED_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        parsed = parse_resume(file_path)
    except Exception as e:
        os.remove(file_path)
        logger.error(f"Resume parse error: {e}")
        raise HTTPException(status_code=422, detail=f"Could not parse resume: {str(e)}")

    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        raw_text=parsed["raw_text"],
        parsed_data=parsed,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "resume_id": resume.id,
        "filename": resume.filename,
        "skills_found": parsed["skills"],
        "word_count": parsed["word_count"],
        "email": parsed["email"],
        "links": parsed["links"],
        "message": "Resume uploaded and parsed successfully",
    }


@router.get("/")
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "skills": (r.parsed_data or {}).get("skills", []),
            "word_count": (r.parsed_data or {}).get("word_count", 0),
            "created_at": r.created_at,
        }
        for r in resumes
    ]


@router.get("/{resume_id}")
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {
        "id": resume.id,
        "filename": resume.filename,
        "parsed_data": resume.parsed_data,
        "raw_text_preview": (resume.raw_text or "")[:500],
        "created_at": resume.created_at,
    }


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted"}
