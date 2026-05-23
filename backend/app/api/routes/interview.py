from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.schemas.analysis import InterviewRequest
from app.services.ai.engine import generate_interview_questions

router = APIRouter()


@router.post("/generate")
def generate_questions(
    data: InterviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate personalized interview questions from resume + optional role."""
    resume = db.query(Resume).filter(Resume.id == data.resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    role_title = data.role_title or "AI/ML Engineer"

    if data.job_id:
        job = db.query(Job).filter(Job.id == data.job_id).first()
        if job:
            role_title = f"{job.title} at {job.company}"

    questions = generate_interview_questions(resume.raw_text, role_title)

    return {
        "resume_id": resume.id,
        "role": role_title,
        "total_questions": len(questions),
        "questions": questions,
        "tip": "Practice answering these out loud. Time yourself — 90 seconds per answer max for technical, 2 minutes for behavioral.",
    }


@router.get("/tips")
def interview_tips():
    """General interview tips for Indian fresher tech interviews."""
    return {
        "rounds": [
            {
                "round": "Online Assessment (OA)",
                "what_to_expect": "DSA problems (2-3), sometimes MCQ on CS fundamentals",
                "prep": "Practice LeetCode Easy-Medium. Focus on arrays, strings, hashmaps, basic DP.",
            },
            {
                "round": "Technical Round 1",
                "what_to_expect": "Core CS concepts, your projects deep-dive, Python/language basics",
                "prep": "Know every line on your resume. Be ready to explain architecture decisions.",
            },
            {
                "round": "Technical Round 2",
                "what_to_expect": "System design basics (for GenAI roles: design a chatbot, RAG system), ML concepts",
                "prep": "Practice explaining your RAG pipeline end to end. Know embeddings, chunking, retrieval.",
            },
            {
                "round": "HR Round",
                "what_to_expect": "Why this company, salary negotiation, notice period, relocation",
                "prep": "Research the company product. Know their tech stack. Have a salary number ready.",
            },
        ],
        "common_mistakes": [
            "Not knowing your own projects deeply — recruiters will probe every claim",
            "Saying 'I used LangChain' without knowing what it does internally",
            "Not asking questions at the end — always ask about the team and tech stack",
            "Negotiating too quickly — wait for the offer, then negotiate",
        ],
        "power_phrases": [
            "I built this end-to-end including deployment at [URL]",
            "The main challenge was X, which I solved by Y, resulting in Z improvement",
            "I tested this approach against baseline and measured improvement using [metric]",
        ],
    }
