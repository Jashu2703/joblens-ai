import time
import random
import httpx
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from loguru import logger


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

RATE_LIMIT_DELAY = (2, 4)  # seconds between requests


def _sleep():
    time.sleep(random.uniform(*RATE_LIMIT_DELAY))


def get_seed_jobs() -> List[Dict[str, Any]]:
    """
    Returns a curated seed dataset of real fresher AI/ML/Python jobs in India.
    Used when scraping is unavailable or as initial DB seed.
    In production, supplement with live scraping.
    """
    return [
        {
            "title": "Junior AI Engineer",
            "company": "Zoho Corporation",
            "location": "Hyderabad",
            "experience_required": "0-1 years",
            "skills_required": ["Python", "Machine Learning", "NLP", "TensorFlow", "SQL"],
            "description": "Build and deploy ML models for enterprise SaaS products. Work with NLP pipelines, model training, and REST APIs. Fresher with strong Python and ML fundamentals preferred.",
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
            "description": "Join our engineering team to build scalable backend services. Strong Python OOP, Django/FastAPI, database design, and API development skills required.",
            "source_url": "https://careers.freshworks.com",
            "source": "seed",
            "salary_range": "5-9 LPA",
            "job_type": "full-time",
        },
        {
            "title": "ML Engineer - Fresher",
            "company": "Walmart Global Tech",
            "location": "Bangalore (Remote OK)",
            "experience_required": "0-1 years",
            "skills_required": ["Python", "Machine Learning", "Scikit-learn", "SQL", "Statistics"],
            "description": "Work on recommendation systems and demand forecasting models. Strong ML fundamentals, Python, and SQL required. Knowledge of feature engineering and model evaluation essential.",
            "source_url": "https://careers.walmart.com",
            "source": "seed",
            "salary_range": "8-14 LPA",
            "job_type": "full-time",
        },
        {
            "title": "GenAI Engineer",
            "company": "PhonePe",
            "location": "Bangalore",
            "experience_required": "0-2 years",
            "skills_required": ["Python", "LLMs", "LangChain", "RAG", "FastAPI", "Vector Databases"],
            "description": "Build GenAI features for fintech products. RAG pipelines, LLM fine-tuning, prompt engineering, and production Python required. FastAPI backend experience is a plus.",
            "source_url": "https://careers.phonepe.com",
            "source": "seed",
            "salary_range": "10-18 LPA",
            "job_type": "full-time",
        },
        {
            "title": "Data Scientist Trainee",
            "company": "Mu Sigma",
            "location": "Hyderabad",
            "experience_required": "0-1 years",
            "skills_required": ["Python", "Statistics", "SQL", "Pandas", "Machine Learning", "Excel"],
            "description": "Analyze large datasets for business intelligence. Strong analytical thinking, Python, SQL, and statistics required. Tableau or Power BI knowledge helpful.",
            "source_url": "https://www.mu-sigma.com/careers",
            "source": "seed",
            "salary_range": "4-6 LPA",
            "job_type": "full-time",
        },
        {
            "title": "AI/ML Intern",
            "company": "Samsung R&D Institute",
            "location": "Bangalore",
            "experience_required": "0 years",
            "skills_required": ["Python", "Deep Learning", "PyTorch", "Computer Vision", "NLP"],
            "description": "6-month internship on AI research projects. Deep learning, PyTorch/TensorFlow, and strong math fundamentals required. Final year B.Tech students preferred.",
            "source_url": "https://research.samsung.com/sri-b/careers",
            "source": "seed",
            "salary_range": "25-40k/month",
            "job_type": "internship",
        },
        {
            "title": "Software Engineer - Python",
            "company": "Razorpay",
            "location": "Bangalore (Remote OK)",
            "experience_required": "0-2 years",
            "skills_required": ["Python", "FastAPI", "Microservices", "PostgreSQL", "Docker", "Redis"],
            "description": "Build payment infrastructure at scale. Strong Python, REST APIs, database design, Docker, and system design fundamentals. DSA proficiency required for interviews.",
            "source_url": "https://razorpay.com/jobs",
            "source": "seed",
            "salary_range": "12-20 LPA",
            "job_type": "full-time",
        },
        {
            "title": "NLP Engineer (Entry Level)",
            "company": "Sprinklr",
            "location": "Gurgaon / Remote",
            "experience_required": "0-2 years",
            "skills_required": ["Python", "NLP", "Hugging Face", "Transformers", "BERT", "Text Classification"],
            "description": "Work on text analytics and sentiment analysis products. NLP fundamentals, Hugging Face, transformer fine-tuning, and Python required. Experience with LLMs is a strong plus.",
            "source_url": "https://www.sprinklr.com/careers",
            "source": "seed",
            "salary_range": "7-12 LPA",
            "job_type": "full-time",
        },
        {
            "title": "Backend Developer - Fresher",
            "company": "Ola",
            "location": "Bangalore",
            "experience_required": "0-1 years",
            "skills_required": ["Python", "Django", "REST APIs", "MySQL", "Git", "Docker"],
            "description": "Build APIs for mobility platform. Strong Python and Django skills, database design, REST API development. Good understanding of OOP and design patterns required.",
            "source_url": "https://www.olacabs.com/careers",
            "source": "seed",
            "salary_range": "6-10 LPA",
            "job_type": "full-time",
        },
        {
            "title": "Data Engineer Intern",
            "company": "Swiggy",
            "location": "Bangalore",
            "experience_required": "0 years",
            "skills_required": ["Python", "SQL", "Apache Spark", "Airflow", "ETL", "PostgreSQL"],
            "description": "Build data pipelines for food-tech analytics. Python, SQL, and data pipeline knowledge required. Spark/Airflow experience is a strong advantage.",
            "source_url": "https://careers.swiggy.com",
            "source": "seed",
            "salary_range": "20-35k/month",
            "job_type": "internship",
        },
        {
            "title": "Junior ML Engineer",
            "company": "Meesho",
            "location": "Bangalore",
            "experience_required": "0-2 years",
            "skills_required": ["Python", "Machine Learning", "Recommendation Systems", "SQL", "A/B Testing"],
            "description": "Build ML models for product recommendations and search ranking. Strong ML fundamentals, Python, SQL, and statistics. Experience with large-scale datasets preferred.",
            "source_url": "https://careers.meesho.com",
            "source": "seed",
            "salary_range": "8-14 LPA",
            "job_type": "full-time",
        },
        {
            "title": "AI Research Intern",
            "company": "Microsoft India",
            "location": "Hyderabad",
            "experience_required": "0 years",
            "skills_required": ["Python", "Deep Learning", "PyTorch", "Research", "Mathematics", "LLMs"],
            "description": "Research internship on large language models and AI systems. Strong math, Python, deep learning, and research aptitude required. Publications or open-source contributions are a plus.",
            "source_url": "https://careers.microsoft.com/india",
            "source": "seed",
            "salary_range": "50-80k/month",
            "job_type": "internship",
        },
        {
            "title": "Full Stack Developer (AI-powered)",
            "company": "Darwinbox",
            "location": "Hyderabad",
            "experience_required": "0-2 years",
            "skills_required": ["Python", "React", "FastAPI", "PostgreSQL", "Docker", "REST APIs"],
            "description": "Build HR tech features with AI integration. Full stack skills — Python backend (FastAPI/Django), React frontend, PostgreSQL, and Docker. AI/ML integration experience is a plus.",
            "source_url": "https://darwinbox.com/careers",
            "source": "seed",
            "salary_range": "6-12 LPA",
            "job_type": "full-time",
        },
        {
            "title": "Prompt Engineer / LLM Developer",
            "company": "Haptik (Jio)",
            "location": "Mumbai / Remote",
            "experience_required": "0-2 years",
            "skills_required": ["Python", "LLMs", "Prompt Engineering", "LangChain", "RAG", "NLP"],
            "description": "Design and optimize prompts for conversational AI products. LLM expertise, prompt engineering, RAG architectures, and Python required. Experience with enterprise chatbots is a plus.",
            "source_url": "https://haptik.ai/careers",
            "source": "seed",
            "salary_range": "6-12 LPA",
            "job_type": "full-time",
        },
        {
            "title": "Python Automation Engineer",
            "company": "Infosys BPM",
            "location": "Pune / Hyderabad",
            "experience_required": "0-1 years",
            "skills_required": ["Python", "Selenium", "REST APIs", "SQL", "Git"],
            "description": "Automate business processes using Python and web automation tools. Strong Python scripting, Selenium, API testing, and SQL required. Good for freshers with strong Python fundamentals.",
            "source_url": "https://careers.infosys.com",
            "source": "seed",
            "salary_range": "3.5-5.5 LPA",
            "job_type": "full-time",
        },
    ]


def scrape_naukri_jobs(query: str = "fresher python AI ML", location: str = "Hyderabad", max_pages: int = 2) -> List[Dict[str, Any]]:
    """
    Scrape Naukri.com for fresher AI/ML/Python jobs.
    Rate-limited and responsible — only public search results.
    """
    jobs = []
    base_url = "https://www.naukri.com"

    for page in range(0, max_pages):
        try:
            url = f"{base_url}/{query.replace(' ', '-')}-jobs-in-{location.lower()}?experience=0"
            if page > 0:
                url += f"&pageNo={page + 1}"

            logger.info(f"Scraping Naukri page {page + 1}: {url}")
            _sleep()

            with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
                response = client.get(url)

            if response.status_code != 200:
                logger.warning(f"Naukri returned {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.find_all("article", class_=lambda x: x and "jobTuple" in x)

            if not job_cards:
                job_cards = soup.find_all("div", attrs={"data-job-id": True})

            logger.info(f"Found {len(job_cards)} job cards on page {page + 1}")

            for card in job_cards[:10]:
                try:
                    title_el = card.find(["a", "h2"], class_=lambda x: x and "title" in str(x).lower())
                    company_el = card.find(class_=lambda x: x and "company" in str(x).lower())
                    location_el = card.find(class_=lambda x: x and "location" in str(x).lower() or "loc" in str(x).lower())
                    skills_el = card.find(class_=lambda x: x and "skill" in str(x).lower() or "tag" in str(x).lower())

                    title = title_el.get_text(strip=True) if title_el else "Software Engineer"
                    company = company_el.get_text(strip=True) if company_el else "Company"
                    loc = location_el.get_text(strip=True) if location_el else location
                    skills_text = skills_el.get_text(separator=",", strip=True) if skills_el else ""
                    skills = [s.strip() for s in skills_text.split(",") if s.strip() and len(s.strip()) < 30]

                    job_url = ""
                    link = title_el.get("href") if title_el and title_el.name == "a" else None
                    if link:
                        job_url = link if link.startswith("http") else base_url + link

                    if title and company:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": loc,
                            "experience_required": "0-2 years",
                            "skills_required": skills[:10],
                            "description": f"{title} at {company}. Skills: {skills_text}",
                            "source_url": job_url,
                            "source": "naukri",
                            "salary_range": "",
                            "job_type": "full-time",
                        })
                except Exception as e:
                    logger.debug(f"Card parse error: {e}")
                    continue

        except Exception as e:
            logger.error(f"Naukri scrape error page {page}: {e}")
            continue

    logger.info(f"Scraped {len(jobs)} jobs from Naukri")
    return jobs
