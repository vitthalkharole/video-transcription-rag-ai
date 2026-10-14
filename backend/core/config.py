
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    DATABASE_URL: str

    GROQ_API_KEY: str
    WHISPER_MODEL: str = "small"
    SARVAM_API_KEY: str
    SARVAM_STT_MODEL: str = "saaras:v2.5"
    GEMINI_API_KEY:str
    JWT_SECRET_KEY:str
    JWT_ALGORITHM:str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES:int

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore"
    )


settings = Settings()
