import httpx
from typing import List, Dict, Any
from loguru import logger
from app.core.config import settings


def fetch_adzuna_jobs(
    keywords: str = "python AI machine learning",
    location: str = "india",
    max_results: int = 50
) -> List[Dict[str, Any]]:
    """Fetch real live jobs from Adzuna API."""
    app_id = getattr(settings, "ADZUNA_APP_ID", None)
    app_key = getattr(settings, "ADZUNA_APP_KEY", None)

    if not app_id or not app_key:
        logger.warning("Adzuna API keys not configured. Using seed jobs.")
        return []

    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": max_results,
        "what": keywords,
        "where": location,
        "content-type": "application/json",
        "sort_by": "date",
    }

    try:
        with httpx.Client(timeout=15) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        jobs = []
        for result in data.get("results", []):
            category = result.get("category", {}).get("label", "")
            company = result.get("company", {}).get("display_name", "Unknown Company")
            location_data = result.get("location", {})
            location_str = ", ".join(location_data.get("area", ["India"])[-2:])
            title = result.get("title", "")
            description = result.get("description", "")
            salary_min = result.get("salary_min")
            salary_max = result.get("salary_max")
            salary = ""
            if salary_min and salary_max:
                salary = f"₹{int(salary_min/1000)}k-{int(salary_max/1000)}k/year"
            elif salary_min:
                salary = f"₹{int(salary_min/1000)}k+/year"

            # Extract skills from description
            skill_keywords = [
                "python", "java", "javascript", "sql", "react", "django",
                "fastapi", "machine learning", "deep learning", "nlp",
                "tensorflow", "pytorch", "docker", "aws", "git",
                "langchain", "llm", "rag", "data science", "postgresql",
                "mongodb", "pandas", "numpy", "scikit-learn", "spark"
            ]
            desc_lower = description.lower()
            skills = [s for s in skill_keywords if s in desc_lower][:8]

            jobs.append({
                "title": title,
                "company": company,
                "location": location_str or "India",
                "experience_required": "0-2 years",
                "skills_required": skills,
                "description": description[:500],
                "source_url": result.get("redirect_url", ""),
                "source": "adzuna",
                "salary_range": salary,
                "job_type": "internship" if "intern" in title.lower() else "full-time",
            })

        logger.info(f"Fetched {len(jobs)} jobs from Adzuna")
        return jobs

    except Exception as e:
        logger.error(f"Adzuna API error: {e}")
        return []


def get_seed_jobs() -> List[Dict[str, Any]]:
    """Try Adzuna first, fall back to seed data."""
    live_jobs = []

    # Try multiple keyword searches
    searches = [
        "python AI engineer fresher",
        "machine learning engineer entry level",
        "data scientist fresher india",
        "generative AI developer",
        "backend python developer fresher",
    ]

    for query in searches:
        jobs = fetch_adzuna_jobs(keywords=query, max_results=10)
        live_jobs.extend(jobs)
        if len(live_jobs) >= 40:
            break

    if live_jobs:
        # Deduplicate by title+company
        seen = set()
        unique_jobs = []
        for job in live_jobs:
            key = f"{job['title']}_{job['company']}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        logger.info(f"Returning {len(unique_jobs)} unique live jobs from Adzuna")
        return unique_jobs

    # Fallback seed data
    logger.warning("Adzuna returned no jobs. Using seed data.")
    return _get_fallback_seeds()


def _get_fallback_seeds() -> List[Dict[str, Any]]:
    return [
        {
            "title": "Junior AI Engineer",
            "company": "Zoho Corporation",
            "location": "Hyderabad",
            "experience_required": "0-1 years",
            "skills_required": ["Python", "Machine Learning", "NLP", "TensorFlow", "SQL"],
            "description": "Build and deploy ML models for enterprise SaaS products.",
            "source_url": "https://careers.zohocorp.com",
            "source": "seed",
            "salary_range": "4-7 LPA",
            "job_type": "full-time",
        },
        {
            "title": "Python Developer (Fresher)",
            "company": "Freshworks",
            "location": "Hyderabad",
            "experience_required": "0-2 years",
            "skills_required": ["Python", "Django", "REST APIs", "PostgreSQL", "Git"],
            "description": "Join our engineering team to build scalable backend services.",
            "source_url": "https://careers.freshworks.com",
            "source": "seed",
            "salary_range": "5-9 LPA",
            "job_type": "full-time",
        },
        {
            "title": "ML Engineer - Fresher",
            "company": "Walmart Global Tech",
            "location": "Bangalore",
            "experience_required": "0-1 years",
            "skills_required": ["Python", "Machine Learning", "Scikit-learn", "SQL"],
            "description": "Work on recommendation systems and demand forecasting.",
            "source_url": "https://careers.walmart.com",
            "source": "seed",
            "salary_range": "8-14 LPA",
            "job_type": "full-time",
        },
    ]