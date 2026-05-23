from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ATSRequest(BaseModel):
    resume_id: int
    jd_text: str


class GapRequest(BaseModel):
    resume_id: int
    jd_text: Optional[str] = None


class RoleMatchRequest(BaseModel):
    resume_id: int
    top_k: int = 10


class InterviewRequest(BaseModel):
    resume_id: int
    job_id: Optional[int] = None
    role_title: Optional[str] = None


class FullAnalysisRequest(BaseModel):
    resume_id: int
    jd_text: Optional[str] = None


class ATSResult(BaseModel):
    score: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    feedback: str
    verdict: str  # "Strong match", "Moderate", "Weak"


class GapResult(BaseModel):
    resume_gaps: List[Dict[str, Any]]
    profile_gaps: List[Dict[str, Any]]
    market_gaps: List[Dict[str, Any]]
    priority_fixes: List[str]


class MatchedRole(BaseModel):
    job_id: int
    title: str
    company: str
    location: str
    similarity_score: float
    match_percentage: int
    skills_matched: List[str]
    skills_missing: List[str]


class InterviewQuestion(BaseModel):
    question: str
    category: str  # technical, behavioral, project-based
    difficulty: str  # easy, medium, hard
    model_answer: str


class FullAnalysisResult(BaseModel):
    analysis_id: int
    ats: Optional[ATSResult]
    gaps: GapResult
    matched_roles: List[MatchedRole]
    interview_questions: List[InterviewQuestion]
