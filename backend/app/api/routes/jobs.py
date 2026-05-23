from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job
from app.services.scraper.job_scraper import get_seed_jobs, scrape_naukri_jobs
from app.services.ai.engine import get_embedding

router = APIRouter()


def seed_jobs_task(db: Session):
    """Background task to seed jobs into DB."""
    try:
        existing_count = db.query(Job).count()
        if existing_count >= 10:
            logger.info(f"DB already has {existing_count} jobs, skipping seed")
            return

        jobs = get_seed_jobs()
        added = 0
        for job_data in jobs:
            existing = db.query(Job).filter(Job.title == job_data["title"], Job.company == job_data["company"]).first()
            if existing:
                continue

            jd_text = f"{job_data['title']} {job_data['company']} {' '.join(job_data.get('skills_required', []))} {job_data.get('description', '')}"
            embedding = get_embedding(jd_text[:1000])

            job = Job(
                title=job_data["title"],
                company=job_data["company"],
                location=job_data.get("location"),
                experience_required=job_data.get("experience_required", "0-2 years"),
                skills_required=job_data.get("skills_required", []),
                description=job_data.get("description"),
                source_url=job_data.get("source_url"),
                source=job_data.get("source", "seed"),
                salary_range=job_data.get("salary_range"),
                job_type=job_data.get("job_type", "full-time"),
                embedding=embedding,
            )
            db.add(job)
            added += 1

        db.commit()
        logger.info(f"Seeded {added} jobs into database")
    except Exception as e:
        logger.error(f"Job seeding error: {e}")
        db.rollback()


@router.post("/seed")
def seed_jobs(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Seed the job database with curated fresher jobs."""
    background_tasks.add_task(seed_jobs_task, db)
    return {"message": "Job seeding started in background. Check /api/jobs in a moment."}


@router.post("/seed/now")
def seed_jobs_now(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Seed jobs synchronously (for testing)."""
    seed_jobs_task(db)
    count = db.query(Job).count()
    return {"message": f"Seeding complete. Total jobs in DB: {count}"}


@router.get("/")
def list_jobs(
    search: Optional[str] = None,
    job_type: Optional[str] = None,
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(Job)

    if search:
        query = query.filter(
            Job.title.ilike(f"%{search}%") | Job.description.ilike(f"%{search}%")
        )
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    total = query.count()
    jobs = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "jobs": [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "skills_required": j.skills_required,
                "salary_range": j.salary_range,
                "job_type": j.job_type,
                "experience_required": j.experience_required,
                "source_url": j.source_url,
            }
            for j in jobs
        ],
    }


@router.get("/stats")
def job_stats(db: Session = Depends(get_db)):
    total = db.query(Job).count()
    return {
        "total_jobs": total,
        "full_time": db.query(Job).filter(Job.job_type == "full-time").count(),
        "internships": db.query(Job).filter(Job.job_type == "internship").count(),
        "status": "seeded" if total > 0 else "empty - call POST /api/jobs/seed/now",
    }
