"""
config.py
---------
Central place for all settings/environment variables.
Every other file imports `settings` from here instead of calling os.getenv() everywhere.
Why: if you deploy or a teammate runs this locally, only .env changes — no code changes.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./gem_compliance.db"

    # LLM (Groq — free tier) - used for document field extraction + recommendation generation
    GROQ_API_KEY: str = ""
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # File storage (local disk for hackathon)
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_BYTES: int = 10485760

    # ML model path
    RISK_MODEL_PATH: str = "./app/ml/risk_model.pkl"

    class Config:
        env_file = ".env"


settings = Settings()
