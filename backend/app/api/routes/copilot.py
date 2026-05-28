from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from loguru import logger
import httpx
from bs4 import BeautifulSoup

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.services.ai.engine import call_llm, safe_parse_json

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────
class TailorRequest(BaseModel):
    resume_id: int
    jd_text: str
    job_title: Optional[str] = "the role"
    company_name: Optional[str] = "the company"


class CoverLetterRequest(BaseModel):
    resume_id: int
    jd_text: str
    job_title: Optional[str] = "the role"
    company_name: Optional[str] = "the company"


class JDFetchRequest(BaseModel):
    url: str


class MockAnswerRequest(BaseModel):
    question: str
    answer: str
    role_title: Optional[str] = "AI/ML Engineer"


class RoadmapRequest(BaseModel):
    resume_id: int
    target_role: str


# ── JD Auto-Fetcher ───────────────────────────────────────
@router.post("/fetch-jd")
def fetch_jd(data: JDFetchRequest):
    """Fetch job description from a URL automatically."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        with httpx.Client(timeout=15, headers=headers, follow_redirects=True) as client:
            response = client.get(data.url)

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        # Try common JD containers
        jd_text = ""
        for selector in [
            ".job-description", ".description", "#job-description",
            "[data-testid='job-description']", ".jobDescriptionText",
            ".jobs-description", ".job-details", "article", "main"
        ]:
            element = soup.select_one(selector)
            if element:
                jd_text = element.get_text(separator="\n", strip=True)
                if len(jd_text) > 200:
                    break

        if not jd_text or len(jd_text) < 200:
            jd_text = soup.get_text(separator="\n", strip=True)
            jd_text = "\n".join(
                line for line in jd_text.split("\n")
                if len(line.strip()) > 30
            )[:3000]

        if len(jd_text) < 100:
            raise HTTPException(status_code=422, detail="Could not extract job description from this URL. Please paste it manually.")

        return {
            "jd_text": jd_text[:3000],
            "char_count": len(jd_text),
            "message": "Job description extracted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not fetch URL: {str(e)}. Please paste the JD manually.")


# ── Resume Tailor ─────────────────────────────────────────
@router.post("/tailor-resume")
def tailor_resume(
    data: TailorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rewrite resume bullets to match the job description."""
    resume = db.query(Resume).filter(
        Resume.id == data.resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    prompt = f"""You are an expert resume writer for Indian tech freshers.

ORIGINAL RESUME:
{resume.raw_text[:2500]}

TARGET JOB: {data.job_title} at {data.company_name}

JOB DESCRIPTION:
{data.jd_text[:2000]}

Rewrite this resume to better match the job description. Return ONLY valid JSON (no markdown):
{{
  "tailored_summary": "<2-3 sentence professional summary tailored to this role>",
  "tailored_bullets": [
    {{
      "section": "internship/project name",
      "original": "<original bullet>",
      "tailored": "<rewritten bullet with keywords from JD, quantified where possible>"
    }}
  ],
  "keywords_added": ["list", "of", "keywords", "added"],
  "ats_improvement": "<brief explanation of how this improves ATS score>"
}}

Rules:
- Keep facts accurate, just reframe with JD keywords
- Add numbers/metrics where reasonable
- Use action verbs from the JD
- Maximum 5-6 tailored bullets
- Keep it honest, not inflated"""

    response = call_llm(prompt)
    result = safe_parse_json(response)

    if not result:
        raise HTTPException(status_code=500, detail="Failed to tailor resume. Try again.")

    return {
        "resume_id": resume.id,
        "job_title": data.job_title,
        "company": data.company_name,
        "tailored_summary": result.get("tailored_summary", ""),
        "tailored_bullets": result.get("tailored_bullets", []),
        "keywords_added": result.get("keywords_added", []),
        "ats_improvement": result.get("ats_improvement", ""),
    }


# ── Cover Letter Generator ────────────────────────────────
@router.post("/cover-letter")
def generate_cover_letter(
    data: CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a personalized cover letter."""
    resume = db.query(Resume).filter(
        Resume.id == data.resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    prompt = f"""You are an expert cover letter writer for Indian tech freshers.

CANDIDATE RESUME:
{resume.raw_text[:2000]}

TARGET ROLE: {data.job_title} at {data.company_name}

JOB DESCRIPTION:
{data.jd_text[:1500]}

Write a compelling, personalized cover letter. Return ONLY valid JSON (no markdown):
{{
  "subject_line": "<email subject line for this application>",
  "cover_letter": "<full cover letter text, 3-4 paragraphs, professional but genuine tone>",
  "word_count": <approximate word count>
}}

Rules:
- Reference specific projects from resume that match JD requirements
- Mention specific technologies from JD that candidate knows
- Sound genuine, not template-like
- For a fresher — show enthusiasm and learning ability
- End with clear call to action
- Keep under 300 words"""

    response = call_llm(prompt)
    result = safe_parse_json(response)

    if not result:
        raise HTTPException(status_code=500, detail="Failed to generate cover letter. Try again.")

    return {
        "resume_id": resume.id,
        "job_title": data.job_title,
        "company": data.company_name,
        "subject_line": result.get("subject_line", f"Application for {data.job_title}"),
        "cover_letter": result.get("cover_letter", ""),
        "word_count": result.get("word_count", 0),
    }


# ── Mock Interview Scorer ─────────────────────────────────
@router.post("/score-answer")
def score_answer(
    data: MockAnswerRequest,
    current_user: User = Depends(get_current_user),
):
    """Score a mock interview answer and give feedback."""
    prompt = f"""You are a senior interviewer at a top Indian tech company hiring for: {data.role_title}

INTERVIEW QUESTION:
{data.question}

CANDIDATE'S ANSWER:
{data.answer}

Evaluate this answer and return ONLY valid JSON (no markdown):
{{
  "score": <integer 1-10>,
  "verdict": "<Excellent|Good|Average|Needs Work>",
  "strengths": ["<what they did well>"],
  "improvements": ["<specific things to improve>"],
  "ideal_answer_hints": "<2-3 key points a great answer would include>",
  "follow_up_question": "<a likely follow-up question based on their answer>"
}}

Be honest but constructive. Score 8+ only for genuinely strong answers."""

    response = call_llm(prompt)
    result = safe_parse_json(response)

    if not result:
        raise HTTPException(status_code=500, detail="Failed to score answer. Try again.")

    return {
        "question": data.question,
        "score": result.get("score", 5),
        "verdict": result.get("verdict", "Average"),
        "strengths": result.get("strengths", []),
        "improvements": result.get("improvements", []),
        "ideal_answer_hints": result.get("ideal_answer_hints", ""),
        "follow_up_question": result.get("follow_up_question", ""),
    }


# ── Skill Gap Roadmap ─────────────────────────────────────
@router.post("/roadmap")
def generate_roadmap(
    data: RoadmapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a personalized skill gap roadmap."""
    resume = db.query(Resume).filter(
        Resume.id == data.resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    prompt = f"""You are a brutally honest career coach for Indian tech freshers in 2026.

CANDIDATE PROFILE:
{resume.raw_text[:2000]}

TARGET ROLE: {data.target_role}

Create a realistic skill gap roadmap. Return ONLY valid JSON (no markdown):
{{
  "current_level": "<honest assessment of current level>",
  "target_level": "<what the target role requires>",
  "gap_score": <integer 1-10, how ready they are>,
  "weeks_to_ready": <realistic weeks needed>,
  "roadmap": [
    {{
      "week": "Week 1-2",
      "focus": "<skill/topic>",
      "tasks": ["<specific task>", "<specific task>"],
      "resources": ["<specific free resource>"]
    }}
  ],
  "must_build": "<one specific project to build during this roadmap>",
  "green_flags": ["<things candidate already has that help>"],
  "red_flags": ["<things that could disqualify them>"]
}}

Be specific and realistic. Reference actual content from their resume."""

    response = call_llm(prompt)
    result = safe_parse_json(response)

    if not result:
        raise HTTPException(status_code=500, detail="Failed to generate roadmap. Try again.")

    return {
        "resume_id": resume.id,
        "target_role": data.target_role,
        "current_level": result.get("current_level", ""),
        "gap_score": result.get("gap_score", 5),
        "weeks_to_ready": result.get("weeks_to_ready", 8),
        "roadmap": result.get("roadmap", []),
        "must_build": result.get("must_build", ""),
        "green_flags": result.get("green_flags", []),
        "red_flags": result.get("red_flags", []),
    }
