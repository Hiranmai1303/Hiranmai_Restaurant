import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
_ENV_FILE: Path = _BASE_DIR / ".env"
if _ENV_FILE.exists():
    load_dotenv(dotenv_path=_ENV_FILE, override=False)

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Restaurant Operations & Review Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # API Keys
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Models
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "google/gemini-2.5-flash")
    ADVANCED_LLM_MODEL: str = os.getenv("ADVANCED_LLM_MODEL", "google/gemini-2.5-pro")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Base paths
    BASE_DIR: Path = _BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    SAMPLE_DATA_DIR: Path = DATA_DIR / "sample_data"
    RAW_DATA_DIR: Path = BASE_DIR / "datasets"
    
    # Storage Paths
    SQLITE_DB_PATH: str = str(PROCESSED_DATA_DIR / "restaurant_operations.db")
    CHROMA_PERSIST_DIR: str = str(PROCESSED_DATA_DIR / "chroma_db")
    
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        extra="allow"
    )

settings = Settings()

