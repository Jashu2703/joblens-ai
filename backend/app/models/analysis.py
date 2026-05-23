from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    # ATS Score
    ats_score = Column(Float)
    jd_text = Column(Text)
    keyword_gaps = Column(JSON)       # missing keywords
    keyword_matches = Column(JSON)    # matched keywords
    ats_feedback = Column(Text)

    # Gap Analysis
    resume_gaps = Column(JSON)        # resume-level issues
    profile_gaps = Column(JSON)       # profile-level issues (experience, projects)
    market_gaps = Column(JSON)        # market-level insights
    gap_priority = Column(JSON)       # ordered list of what to fix first

    # Role Matching
    matched_roles = Column(JSON)      # top matching job IDs with scores

    # Interview Prep
    interview_questions = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="analyses")
    resume = relationship("Resume", back_populates="analyses")
