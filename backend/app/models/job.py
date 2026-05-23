from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float
from sqlalchemy.sql import func
from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False)
    location = Column(String)
    experience_required = Column(String, default="0-2 years")
    skills_required = Column(JSON)  # list of skills
    description = Column(Text)
    source_url = Column(String)
    source = Column(String, default="naukri")  # naukri, linkedin, internshala
    salary_range = Column(String)
    job_type = Column(String, default="full-time")  # full-time, internship
    embedding = Column(JSON)  # stored as list for FAISS
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
