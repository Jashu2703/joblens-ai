import json
import re
from typing import List, Dict, Any, Optional
from loguru import logger
import numpy as np

from app.core.config import settings


def get_llm_client():
    """Get configured LLM client - Gemini preferred, OpenAI fallback."""
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            return genai.GenerativeModel("gemini-2.0-flash"), "gemini"
        except Exception as e:
            logger.warning(f"Gemini init failed: {e}")

    if settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            return client, "openai"
        except Exception as e:
            logger.warning(f"OpenAI init failed: {e}")

    logger.warning("No LLM API key configured. Using mock responses.")
    return None, "mock"


def call_llm(prompt: str) -> str:
    """Call LLM via OpenRouter -> Gemini -> Mock fallback."""
    import httpx

    # ----------------------------
    # 1. Try OpenRouter
    # ----------------------------
    openrouter_key = getattr(
        settings,
        "OPENROUTER_API_KEY",
        None
    )

    if openrouter_key:
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization":
                            f"Bearer {openrouter_key}",
                        "Content-Type":
                            "application/json",
                        "HTTP-Referer":
                            "https://joblens-ai-nine.vercel.app",
                        "X-Title":
                            "JobLens AI"
                    },
                    json={
                        "model":
                            "meta-llama/llama-3.1-8b-instruct:free",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 2000,
                    },
                )

                data = response.json()

                logger.warning(
                    f"OPENROUTER RESPONSE: {data}"
                )

                if "choices" in data:
                    return (
                        data["choices"][0]
                        ["message"]["content"]
                    )

                raise Exception(
                    data.get("error", {})
                    .get(
                        "message",
                        "Unknown OpenRouter error"
                    )
                )

        except Exception as e:
            logger.warning(
                f"OpenRouter failed: {e}"
            )

    # ----------------------------
    # 2. Try Gemini REST
    # ----------------------------
    gemini_key = getattr(
        settings,
        "GEMINI_API_KEY",
        None
    )

    if gemini_key:
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}",
                    headers={
                        "Content-Type":
                            "application/json"
                    },
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {
                                        "text": prompt
                                    }
                                ]
                            }
                        ]
                    },
                )

                data = response.json()

                logger.warning(
                    f"GEMINI RESPONSE: {data}"
                )

                if "candidates" in data:
                    return (
                        data["candidates"][0]
                        ["content"]["parts"][0]
                        ["text"]
                    )

                raise Exception(
                    data.get("error", {})
                    .get(
                        "message",
                        "Unknown Gemini error"
                    )
                )

        except Exception as e:
            logger.warning(
                f"Gemini failed: {e}"
            )

    # ----------------------------
    # 3. Mock fallback
    # ----------------------------
    logger.warning(
        "All LLM providers failed. "
        "Using mock."
    )

    return _mock_response(prompt)


def _mock_response(prompt: str) -> str:
    """Mock response when no API key is configured."""
    if "ats" in prompt.lower() or "score" in prompt.lower():
        return json.dumps({
            "score": 62,
            "matched_keywords": ["python", "fastapi", "machine learning"],
            "missing_keywords": ["docker", "kubernetes", "system design"],
            "feedback": "Your resume shows strong Python and ML skills. Add Docker and deployment experience to improve ATS match.",
            "verdict": "Moderate"
        })
    elif "gap" in prompt.lower():
        return json.dumps({
            "resume_gaps": [
                {"issue": "Bullet points lack quantified results", "severity": "high", "fix": "Add metrics like '97.1% accuracy' or 'reduced latency by 40%'"},
                {"issue": "No deployment/production evidence", "severity": "high", "fix": "Add live URLs or mention deployment platforms used"}
            ],
            "profile_gaps": [
                {"issue": "Internship brands are not recognizable", "severity": "high", "fix": "Target internships at product companies or well-known startups"},
                {"issue": "GitHub has sparse commit history", "severity": "medium", "fix": "Commit daily — even small improvements count"}
            ],
            "market_gaps": [
                {"issue": "LLM/GenAI market demands Agentic AI skills", "severity": "medium", "fix": "Learn LangGraph and build a multi-agent project"},
                {"issue": "Most fresher roles now require Docker basics", "severity": "medium", "fix": "Dockerize all your projects"}
            ],
            "priority_fixes": [
                "Add live deployment URLs to all projects",
                "Quantify every bullet point with numbers",
                "Clean up GitHub — READMEs, commit history, no forks",
                "Build one flagship project with real users",
                "Apply only to CGPA-filter-free startups and product companies"
            ]
        })
    elif "interview" in prompt.lower():
        return json.dumps([
            {"question": "Explain how RAG reduces LLM hallucinations.", "category": "technical", "difficulty": "medium", "model_answer": "RAG grounds LLM responses in retrieved documents. Instead of relying on parametric memory which can hallucinate, we retrieve relevant chunks from a vector store and inject them into the prompt context. The LLM then generates answers based on this grounded context, reducing fabrication significantly."},
            {"question": "Walk me through how you'd deploy a FastAPI app to production.", "category": "technical", "difficulty": "medium", "model_answer": "I'd containerize it with Docker, write a docker-compose.yml for local dev with PostgreSQL and the API service, push to GitHub, then deploy on Railway or Render with environment variables set via their dashboard. I'd add health check endpoints and use GitHub Actions for CI."},
            {"question": "Tell me about a time your model failed and how you fixed it.", "category": "behavioral", "difficulty": "easy", "model_answer": "In my spam classifier, initial accuracy was 89%. I analyzed false positives and found TF-IDF was weighting common words too heavily. I added stop word filtering and tuned the Naive Bayes alpha parameter, improving accuracy to 97.1%."}
        ])
    return '{"result": "mock response"}'


def safe_parse_json(text: str) -> Any:
    """Safely parse JSON from LLM response, handling markdown code blocks."""
    text = text.strip()
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        json_match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
    return None


def compute_ats_score(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """Compute ATS score using LLM + keyword analysis."""
    prompt = f"""You are an expert ATS (Applicant Tracking System) analyzer for Indian tech companies.

RESUME TEXT:
{resume_text[:3000]}

JOB DESCRIPTION:
{jd_text[:2000]}

Analyze the resume against the job description and return ONLY a valid JSON object (no markdown, no explanation):
{{
  "score": <integer 0-100>,
  "matched_keywords": ["list", "of", "matched", "keywords"],
  "missing_keywords": ["list", "of", "missing", "important", "keywords"],
  "feedback": "<2-3 sentence actionable feedback>",
  "verdict": "<one of: Strong match, Moderate match, Weak match>"
}}

Be strict. Score above 75 only if the resume clearly matches 70%+ of requirements."""

    response = call_llm(prompt)
    result = safe_parse_json(response)

    if not result:
        result = {
            "score": 50,
            "matched_keywords": [],
            "missing_keywords": [],
            "feedback": "Could not fully analyze. Please check your API key.",
            "verdict": "Moderate match"
        }

    return result


def analyze_gaps(resume_text: str, jd_text: Optional[str] = None) -> Dict[str, Any]:
    """Identify resume, profile, and market gaps."""
    jd_section = f"\nJOB DESCRIPTION:\n{jd_text[:1500]}" if jd_text else ""

    prompt = f"""You are a brutally honest career advisor for Indian tech freshers in 2025-26.

RESUME:
{resume_text[:3000]}{jd_section}

Analyze this fresher's profile and return ONLY valid JSON (no markdown):
{{
  "resume_gaps": [
    {{"issue": "<specific resume formatting/content issue>", "severity": "high|medium|low", "fix": "<specific actionable fix>"}}
  ],
  "profile_gaps": [
    {{"issue": "<experience/project/skill gap>", "severity": "high|medium|low", "fix": "<specific actionable fix>"}}
  ],
  "market_gaps": [
    {{"issue": "<market trend or demand gap>", "severity": "high|medium|low", "fix": "<specific actionable fix>"}}
  ],
  "priority_fixes": ["<ordered list of top 5 most impactful things to fix>"]
}}

Be specific. Reference actual content from the resume. Do not be generic."""

    response = call_llm(prompt)
    result = safe_parse_json(response)

    if not result:
        result = {
            "resume_gaps": [{"issue": "Could not analyze", "severity": "medium", "fix": "Check API configuration"}],
            "profile_gaps": [],
            "market_gaps": [],
            "priority_fixes": ["Configure API key for full analysis"]
        }

    return result


def generate_interview_questions(resume_text: str, role_title: str = "AI/ML Engineer") -> List[Dict[str, Any]]:
    """Generate personalized interview questions based on resume."""
    prompt = f"""You are an interviewer at a top Indian tech company hiring for: {role_title}

CANDIDATE RESUME:
{resume_text[:2500]}

Generate 10 interview questions tailored to THIS candidate's specific resume.
Include technical questions about their actual projects, behavioral questions, and tricky follow-ups.
Return ONLY a valid JSON array (no markdown):
[
  {{
    "question": "<specific question referencing their resume>",
    "category": "technical|behavioral|project-based|hr",
    "difficulty": "easy|medium|hard",
    "model_answer": "<detailed model answer 2-4 sentences>"
  }}
]

Make questions specific to their projects (RAG chatbot, spam classifier etc.), not generic."""

    response = call_llm(prompt)
    result = safe_parse_json(response)

    if not result or not isinstance(result, list):
        result = [
            {
                "question": "Walk me through your RAG pipeline architecture.",
                "category": "project-based",
                "difficulty": "medium",
                "model_answer": "Start with document ingestion, chunking strategy, embedding generation using sentence transformers, FAISS indexing, then retrieval with MMR or similarity search, and finally prompt assembly with retrieved context passed to the LLM."
            }
        ]

    return result


try:
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("Embedding model loaded successfully")
except Exception as e:
    logger.warning(f"Failed to load embedding model: {e}")
    embedding_model = None


def get_embedding(text: str) -> List[float]:
    """Get text embedding using sentence-transformers."""
    try:
        if embedding_model is None:
            raise Exception("Embedding model unavailable")

        embedding = embedding_model.encode(
            text,
            show_progress_bar=False
        )
        return embedding.tolist()

    except Exception as e:
        logger.warning(
            f"Embedding failed: {e}. Using random embedding for demo."
        )
        return list(np.random.rand(384).astype(float))


def compute_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Cosine similarity between two vectors."""
    a = np.array(vec1)
    b = np.array(vec2)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def match_roles(resume_text: str, jobs: List[Any], top_k: int = 10) -> List[Dict[str, Any]]:
    """Match resume against job database using embeddings."""
    resume_embedding = get_embedding(resume_text[:2000])
    resume_skills = set(re.findall(
        r"\b(python|fastapi|django|react|sql|docker|langchain|rag|nlp|machine learning|"
        r"deep learning|tensorflow|pytorch|scikit-learn|aws|git|postgresql)\b",
        resume_text.lower()
    ))

    results = []
    for job in jobs:
        if job.embedding:
            score = compute_similarity(resume_embedding, job.embedding)
        else:
            jd_embedding = get_embedding((job.description or "") + " " + " ".join(job.skills_required or []))
            score = compute_similarity(resume_embedding, jd_embedding)

        job_skills = set(s.lower() for s in (job.skills_required or []))
        matched_skills = list(resume_skills & job_skills)
        missing_skills = list(job_skills - resume_skills)

        results.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location or "Remote/Hyderabad",
            "similarity_score": round(score, 4),
            "match_percentage": min(100, int(score * 140)),
            "skills_matched": matched_skills,
            "skills_missing": missing_skills[:5],
            "source_url": job.source_url,
            "salary_range": job.salary_range,
        })

    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:top_k]
