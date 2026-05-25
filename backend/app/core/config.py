from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://joblens:joblens_secret@localhost:5432/joblens_db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    ADZUNA_APP_ID: Optional[str] = None
    ADZUNA_APP_KEY: Optional[str] = None

    ENVIRONMENT: str = "development"
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
