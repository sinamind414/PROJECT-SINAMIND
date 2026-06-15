# config.py
# Khawarizmi Pro — Configuration centralisée avec validation

from pathlib import Path
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).parent.absolute()
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    debug: bool = False

    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600

    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    OPENAI_FALLBACK_API_KEY: str = ""
    REAL_OPENAI_API_KEY: str = ""
    ia_temperature: float = 0.3
    ia_max_tokens: int = 600
    AI_MODEL_PRIMARY: str = "gemini-2.5-flash"

    SENTRY_DSN: str = ""

    ALLOWED_ORIGINS: List[str] = [
        "https://khawarizmi.dz",
        "https://www.khawarizmi.dz",
        "http://localhost:3000"
    ]

    data_dir: str = ""

    chargily_secret_key: str = ""
    CHARGILY_API_KEY: str = ""
    CHARGILY_SECRET: str = ""

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        if not v:
            raise ValueError(
                "SECRET_KEY non défini. Arrêt du serveur pour sécurité."
            )
        if len(str(v)) < 16:
            raise ValueError(
                "SECRET_KEY trop court. Minimum 16 caractères requis."
            )
        return v

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()


def get_settings() -> Settings:
    return settings


def init_sentry():
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        if settings.SENTRY_DSN:
            sentry_sdk.init(dsn=settings.SENTRY_DSN,
                            integrations=[FastApiIntegration()],
                            traces_sample_rate=0.2,
                            environment=settings.ENVIRONMENT,
                            release=f"khawarizmi-pro@{settings.VERSION}")
    except ImportError:
        pass


def get_allowed_origins() -> List[str]:
    import os
    base_origins = [
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:3000",
        "https://khawarizmi-ia.vercel.app",
        "https://khawarizmi.vercel.app",
        "https://ia-khawarizmi.dz",
        "https://www.ia-khawarizmi.dz",
    ]
    env_value = os.getenv("ALLOWED_ORIGINS", "")
    extra_origins = [
        o.strip()
        for o in env_value.split(",")
        if o.strip() and o.strip().startswith("http")
    ]
    all_origins = list(set(base_origins + extra_origins))
    return all_origins
