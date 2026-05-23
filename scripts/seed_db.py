"""
Run this script to seed the job database directly without Docker.
Usage: python scripts/seed_db.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import SessionLocal, Base, engine
from app.models.job import Job
from app.services.scraper.job_scraper import get_seed_jobs
from app.services.ai.engine import get_embedding

Base.metadata.create_all(bind=engine)
db = SessionLocal()

jobs = get_seed_jobs()
added = 0
for j in jobs:
    exists = db.query(Job).filter(Job.title == j["title"], Job.company == j["company"]).first()
    if exists:
        continue
    text = f"{j['title']} {j['company']} {' '.join(j.get('skills_required', []))}"
    job = Job(**{k: v for k, v in j.items()}, embedding=get_embedding(text[:500]))
    db.add(job)
    added += 1

db.commit()
db.close()
print(f"Seeded {added} jobs successfully.")
