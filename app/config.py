"""Application configuration module."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root if present
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "AI Image Understanding & Content Matching Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "t")
    
    # Storage settings
    DATA_DIR: Path = ROOT_DIR / "data"
    CORPUS_DIR: Path = ROOT_DIR / "data" / "corpus"
    DATABASE_PATH: Path = ROOT_DIR / "data" / "database.sqlite3"
    
    # AI Provider settings
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "offline").lower()  # 'gemini' or 'offline'
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_VISION_MODEL: str = os.getenv("GEMINI_VISION_MODEL", "gemini-1.5-flash")
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    
    # Mismatch Guard Thresholds
    MIN_CONFIDENCE_THRESHOLD: float = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.70"))
    MIN_SIMILARITY_THRESHOLD: float = float(os.getenv("MIN_SIMILARITY_THRESHOLD", "0.60"))
    CONFIDENT_SIMILARITY_THRESHOLD: float = float(os.getenv("CONFIDENT_SIMILARITY_THRESHOLD", "0.75"))
    
    # Background Processing
    MAX_BATCH_RETRIES: int = int(os.getenv("MAX_BATCH_RETRIES", "3"))
    RETRY_BACKOFF_SECONDS: float = float(os.getenv("RETRY_BACKOFF_SECONDS", "0.5"))

settings = Settings()
