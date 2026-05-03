import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://firai:firai_secret@db:5432/firai_db"

    # AI Services
    GEMINI_API_KEY: str = ""  # DEPRECATED — FirAI now uses custom AI engine
    BHASHINI_API_KEY: str = ""
    BHASHINI_USER_ID: str = ""

    # Google Maps
    GOOGLE_MAPS_API_KEY: str = ""

    # Paths
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data")
    STORAGE_DIR: str = os.path.join(os.path.dirname(__file__), "storage")
    RAW_PDFS_DIR: str = os.path.join(os.path.dirname(__file__), "data", "raw_pdfs")
    STRUCTURED_DIR: str = os.path.join(os.path.dirname(__file__), "data", "structured")

    # Custom AI Engine
    LOCAL_MODEL_DIR: str = os.path.join(os.path.dirname(__file__), "ai_engine", "trained_models")

    # Embedding model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
