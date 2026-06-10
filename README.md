# JobLens AI 🔍
**AI-powered job search intelligence for Indian freshers** — ATS scoring, gap analysis, role matching, and interview prep in one platform.

**Stack:** FastAPI · LangChain · Gemini AI · FAISS · PostgreSQL · React · Docker

🔗 **Live:** [joblens-ai-nine.vercel.app](https://joblens-ai-nine.vercel.app)

---

## What it solves

| Pain | Solution |
|---|---|
| Apply 50 times, hear nothing | ATS score + exact keyword gaps vs the JD |
| Don't know which roles fit | Semantic role matching against real fresher jobs |
| Resume vs profile vs market — which is broken? | 3-layer gap analysis with priority fixes |
| Interviews feel like black boxes | AI questions tailored to YOUR resume |

---

## Quick Start

### 1. Get a free Gemini API key
[https://aistudio.google.com](https://aistudio.google.com) → Get API key (free)

### 2. Clone and configure
```bash
git clone https://github.com/Jashu2703/joblens-ai.git
cd joblens-ai
cp .env.example .env
# Open .env and paste your GEMINI_API_KEY
```

### 3. Run
```bash
docker-compose up --build
```

- App: http://localhost:3000
- API docs: http://localhost:8000/docs

### 4. First time setup
1. Register at `http://localhost:3000/register`
2. Upload your resume (PDF or DOCX)
3. Dashboard → click **Seed Jobs Now**
4. Analyze → **Run Full Analysis**

---

## Features

- 📄 Resume upload + skill extraction (PDF/DOCX)
- 🎯 ATS scorer — 0–100 score against any JD
- 🔍 Gap analyzer — resume, profile, and market gaps
- 🤝 Role matcher — FAISS semantic search against job DB
- 🎤 Interview prep — 10 personalized questions + model answers
- 🔐 JWT auth — secure accounts, history saved

---

## Project Structure

```
joblens-ai/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # auth, resume, jobs, analyze, interview
│   │   ├── core/             # config, database, security
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/ai/      # LLM engine, embeddings, matching
│   │   ├── services/scraper/ # Job scraper
│   │   └── utils/            # Resume parser
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/            # Dashboard, Analyze, Jobs, Interview
│   │   ├── components/       # Navbar
│   │   └── services/api.js   # Axios API client
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Env Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Free at aistudio.google.com |
| `SECRET_KEY` | Yes | Any random string for JWT |
| `DATABASE_URL` | Auto | Set by docker-compose |

---

<img width="705" height="780" alt="image" src="https://github.com/user-attachments/assets/04cf5564-2604-4e8a-a9c9-d4e7a2b7d282" />
<img width="1900" height="922" alt="image" src="https://github.com/user-attachments/assets/dcd93702-d734-4d56-bd4f-27d45c305192" />
<img width="1838" height="924" alt="image" src="https://github.com/user-attachments/assets/ef1dd133-5f3e-43d1-a433-d785b6507d74" />
<img width="1868" height="915" alt="image" src="https://github.com/user-attachments/assets/dc1979d6-da02-4ee1-bb0d-26d61d71777f" />


## Resume Bullet *(copy this)*

> Built and deployed JobLens AI — end-to-end AI job search platform for Indian freshers. ATS scoring via semantic embeddings, 3-layer gap analysis via LLM, role matching with FAISS, personalized interview Q generation. Stack: FastAPI · LangChain · Gemini · FAISS · PostgreSQL · React · Docker.

---

## Built by

**Jashwanth Valasa** — AI/ML Engineer  
[LinkedIn](https://linkedin.com/in/jashwanth-valasa) · [GitHub](https://github.com/Jashu2703)
