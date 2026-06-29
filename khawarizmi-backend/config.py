# config.py
# Khawarizmi Pro — Configuration centralisée avec validation

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).parent.absolute()
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    debug: bool = False

    SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    DATABASE_URL: str = "postgresql+asyncpg://postgres:test@localhost/khawarizmi_test"
    REDIS_URL: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600

    # ── IA — Configuration ────────────────────────────────────────
    # Convention : OPENAI_API_KEY + openai_base_url + openai_model
    # Auto-détection dans lifespan.py :
    #   - gsk_*  → Groq (base_url override)
    #   - AIza*  → Gemini (base_url override)
    # Les anciens GEMINI_API_KEY / REAL_OPENAI_API_KEY sont legacy.
    GEMINI_API_KEY: str = ""  # DEPRECATED — utiliser OPENAI_API_KEY + AIza*
    OPENAI_API_KEY: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    OPENAI_FALLBACK_API_KEY: str = ""
    REAL_OPENAI_API_KEY: str = ""  # DEPRECATED — utiliser OPENAI_API_KEY
    ia_temperature: float = 0.3
    ia_max_tokens: int = 600
    AI_MODEL_PRIMARY: str = "gemini-2.5-flash"

    VISION_API_KEY: str = ""
    vision_base_url: str = "https://api.openai.com/v1"
    vision_model: str = "gpt-4o-mini"

    # ── Z.AI / GLM-4.7 ──────────────────────────────────────────
    ZAI_API_KEY: str = ""
    zai_model: str = "glm-4.7"
    zai_base_url: str = "https://api.z.ai/api/paas/v4/"

    CLOUDFLARE_ACCOUNT_ID: str = ""
    CLOUDFLARE_API_TOKEN: str = ""

    # ── ZenMux GLM ──────────────────────────────────────────────
    ZENMUX_API_KEY: str = ""
    zenmux_base_url: str = "https://zenmux.ai/api/v1"
    zenmux_model: str = "z-ai/glm-5.2-free"

    # ── NaraRouter (proxy OpenAI-compatible) ────────────────────
    NARA_API_KEY: str = ""
    nara_base_url: str = "https://router.bynara.id/v1"
    nara_model: str = "deepseek-v4-flash"

    SENTRY_DSN: str = ""

    ALLOWED_ORIGINS: str = ""

    data_dir: str = ""

    chargily_secret_key: str = ""
    CHARGILY_API_KEY: str = ""
    CHARGILY_SECRET: str = ""

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v):
        import os

        env = os.getenv("ENVIRONMENT", "")
        if env in ("test", "ci"):
            return v or "ci-test-key-for-smoke-tests-only"
        if not v or v.startswith("ci-fallback"):
            raise ValueError("SECRET_KEY non défini. Arrêt du serveur pour sécurité.")
        if len(str(v)) < 16:
            raise ValueError("SECRET_KEY trop court. Minimum 16 caractères requis.")
        return v

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE), env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


settings = Settings()


def get_settings() -> Settings:
    return settings


def init_sentry():
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration

        if settings.SENTRY_DSN:
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[FastApiIntegration()],
                traces_sample_rate=0.2,
                environment=settings.ENVIRONMENT,
                release=f"khawarizmi-pro@{settings.VERSION}",
            )
    except ImportError:
        pass


def get_allowed_origins() -> list[str]:
    base_origins = [
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:3000",
        "https://khawarizmi-ia.vercel.app",
        "https://khawarizmi.vercel.app",
        "https://khawarizmi-ia.netlify.app",
        "https://ia-khawarizmi.dz",
        "https://www.ia-khawarizmi.dz",
    ]
    env_value = settings.ALLOWED_ORIGINS
    extra_origins = [o.strip() for o in env_value.split(",") if o.strip() and o.strip().startswith("http")]
    all_origins = list(set(base_origins + extra_origins))
    return all_origins
