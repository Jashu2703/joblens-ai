from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from loguru import logger

from app.core.database import engine, Base
from app.api.routes import auth, resume, jobs, analyze, interview, copilot
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting JobLens AI...")
    Base.metadata.create_all(bind=engine)
    os.makedirs("uploads", exist_ok=True)
    logger.info("Database tables created. Server ready.")
    yield
    logger.info("Shutting down JobLens AI.")


app = FastAPI(
    title="JobLens AI",
    description="AI-powered job search intelligence for Indian freshers",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analysis"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview Prep"])
app.include_router(copilot.router, prefix="/api/copilot", tags=["AI Copilot"])


@app.get("/", tags=["Health"])
def root():
    return {
        "app": "JobLens AI",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
