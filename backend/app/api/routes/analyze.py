from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.analysis import Analysis
from app.schemas.analysis import ATSRequest, GapRequest, RoleMatchRequest, FullAnalysisRequest
from app.services.ai.engine import compute_ats_score, analyze_gaps, match_roles

router = APIRouter()


def get_resume_or_404(resume_id: int, user_id: int, db: Session) -> Resume:
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not resume.raw_text:
        raise HTTPException(status_code=422, detail="Resume has no parsed text")
    return resume


@router.post("/ats")
def ats_score(
    data: ATSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Score resume against a job description."""
    resume = get_resume_or_404(data.resume_id, current_user.id, db)

    logger.info(f"Computing ATS score for resume {resume.id}")
    result = compute_ats_score(resume.raw_text, data.jd_text)

    return {
        "resume_id": resume.id,
        "filename": resume.filename,
        "ats_score": result.get("score"),
        "matched_keywords": result.get("matched_keywords", []),
        "missing_keywords": result.get("missing_keywords", []),
        "feedback": result.get("feedback"),
        "verdict": result.get("verdict"),
    }


@router.post("/gaps")
def gap_analysis(
    data: GapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Identify resume, profile, and market gaps."""
    resume = get_resume_or_404(data.resume_id, current_user.id, db)

    logger.info(f"Running gap analysis for resume {resume.id}")
    result = analyze_gaps(resume.raw_text, data.jd_text)

    return {
        "resume_id": resume.id,
        "resume_gaps": result.get("resume_gaps", []),
        "profile_gaps": result.get("profile_gaps", []),
        "market_gaps": result.get("market_gaps", []),
        "priority_fixes": result.get("priority_fixes", []),
    }


@router.post("/match-roles")
def match_roles_endpoint(
    data: RoleMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Match resume against job database and return top fits."""
    resume = get_resume_or_404(data.resume_id, current_user.id, db)

    jobs = db.query(Job).all()
    if not jobs:
        return {
            "message": "No jobs in database yet. Call POST /api/jobs/seed/now first.",
            "matched_roles": [],
            "total_jobs_checked": 0,
        }

    logger.info(f"Matching resume {resume.id} against {len(jobs)} jobs")
    matches = match_roles(resume.raw_text, jobs, top_k=data.top_k)

    return {
        "resume_id": resume.id,
        "total_jobs_checked": len(jobs),
        "top_matches": matches,
    }


@router.post("/full")
def full_analysis(
    data: FullAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run complete analysis: ATS score + gap analysis + role matching.
    This is the main endpoint — single call, full intelligence report.
    """
    resume = get_resume_or_404(data.resume_id, current_user.id, db)
    logger.info(f"Running full analysis for user {current_user.id}, resume {resume.id}")

    # ATS Score (only if JD provided)
    ats_result = None
    if data.jd_text:
        ats_result = compute_ats_score(resume.raw_text, data.jd_text)

    # Gap Analysis
    gap_result = analyze_gaps(resume.raw_text, data.jd_text)

    # Role Matching
    jobs = db.query(Job).all()
    matched_roles = match_roles(resume.raw_text, jobs, top_k=10) if jobs else []

    # Save to DB
    analysis = Analysis(
        user_id=current_user.id,
        resume_id=resume.id,
        jd_text=data.jd_text,
        ats_score=ats_result.get("score") if ats_result else None,
        keyword_gaps=ats_result.get("missing_keywords") if ats_result else [],
        keyword_matches=ats_result.get("matched_keywords") if ats_result else [],
        ats_feedback=ats_result.get("feedback") if ats_result else None,
        resume_gaps=gap_result.get("resume_gaps", []),
        profile_gaps=gap_result.get("profile_gaps", []),
        market_gaps=gap_result.get("market_gaps", []),
        gap_priority=gap_result.get("priority_fixes", []),
        matched_roles=matched_roles,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "analysis_id": analysis.id,
        "resume_id": resume.id,
        "filename": resume.filename,
        "ats": {
            "score": ats_result.get("score") if ats_result else None,
            "matched_keywords": ats_result.get("matched_keywords", []) if ats_result else [],
            "missing_keywords": ats_result.get("missing_keywords", []) if ats_result else [],
            "feedback": ats_result.get("feedback") if ats_result else "No JD provided for ATS scoring",
            "verdict": ats_result.get("verdict") if ats_result else "N/A",
        },
        "gaps": {
            "resume_gaps": gap_result.get("resume_gaps", []),
            "profile_gaps": gap_result.get("profile_gaps", []),
            "market_gaps": gap_result.get("market_gaps", []),
            "priority_fixes": gap_result.get("priority_fixes", []),
        },
        "matched_roles": matched_roles,
        "total_jobs_in_db": len(jobs),
    }


@router.get("/history")
def analysis_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all past analyses for the current user."""
    analyses = (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": a.id,
            "resume_id": a.resume_id,
            "ats_score": a.ats_score,
            "priority_fixes_count": len(a.gap_priority or []),
            "matched_roles_count": len(a.matched_roles or []),
            "created_at": a.created_at,
        }
        for a in analyses
    ]
