import re
import os
from typing import Dict, Any, Optional
from loguru import logger

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    text = ""
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
    return text.strip()


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def extract_email(text: str) -> Optional[str]:
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    match = re.search(r"(\+91[\s\-]?)?[6-9]\d{9}", text)
    return match.group(0) if match else None


def extract_links(text: str) -> Dict[str, str]:
    links = {}
    github = re.search(r"github\.com/[\w\-]+", text, re.IGNORECASE)
    linkedin = re.search(r"linkedin\.com/in/[\w\-]+", text, re.IGNORECASE)
    if github:
        links["github"] = "https://" + github.group(0)
    if linkedin:
        links["linkedin"] = "https://" + linkedin.group(0)
    return links


SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c", "sql", "r",
    "fastapi", "django", "flask", "react", "nodejs", "express", "spring",
    "tensorflow", "pytorch", "keras", "scikit-learn", "langchain", "hugging face",
    "llm", "rag", "nlp", "machine learning", "deep learning", "generative ai",
    "faiss", "chromadb", "openai", "gemini", "prompt engineering", "embeddings",
    "docker", "kubernetes", "git", "github", "aws", "gcp", "azure",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "pandas", "numpy", "matplotlib", "power bi", "tableau",
    "apache spark", "pyspark", "airflow", "mlflow", "kafka",
    "rest api", "graphql", "microservices", "ci/cd", "github actions",
]


def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        if skill.lower() in text_lower:
            found.append(skill)
    return list(set(found))


def extract_education(text: str) -> list:
    education = []
    patterns = [
        r"(B\.?Tech|B\.?E|M\.?Tech|M\.?Sc|B\.?Sc|MBA|BCA|MCA|Ph\.?D)[^\n]*",
        r"(Bachelor|Master|Doctor)[^\n]*",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        education.extend(matches)
    return list(set(education))


def extract_experience_years(text: str) -> str:
    if any(word in text.lower() for word in ["fresher", "0 year", "no experience"]):
        return "0"
    match = re.search(r"(\d+)\+?\s*year", text, re.IGNORECASE)
    return match.group(1) if match else "0"


def parse_resume(file_path: str) -> Dict[str, Any]:
    raw_text = extract_text(file_path)
    parsed = {
        "raw_text": raw_text,
        "email": extract_email(raw_text),
        "phone": extract_phone(raw_text),
        "links": extract_links(raw_text),
        "skills": extract_skills(raw_text),
        "education": extract_education(raw_text),
        "experience_years": extract_experience_years(raw_text),
        "word_count": len(raw_text.split()),
        "char_count": len(raw_text),
    }
    logger.info(f"Parsed resume: {len(parsed['skills'])} skills found, {parsed['word_count']} words")
    return parsed
