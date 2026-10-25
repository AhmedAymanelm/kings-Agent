"""
config.py — App settings loaded from environment variables / .env file
"""
from __future__ import annotations
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# Look for .env in backend/ first, then project root
_HERE = Path(__file__).parent          # backend/
_ROOT = _HERE.parent                   # project root
_ENV_FILE = _HERE / ".env" if (_HERE / ".env").exists() else (_ROOT / ".env" if (_ROOT / ".env").exists() else None)

def _get_default_db_url() -> str:
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("LAMBDA_TASK_ROOT"):
        return "sqlite:////tmp/elmloook.db"
    return "sqlite:///./elmloook.db"


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "AI Agent Dashboard"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = _get_default_db_url()

    # ── AI Provider ───────────────────────────────────────
    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"
    AI_TEMPERATURE: float = 0.3
    AI_MAX_TOKENS: int = 512

    # ── WhatsApp Business API ─────────────────────────────
    WA_PHONE_NUMBER_ID: str = ""
    WA_ACCESS_TOKEN: str = ""
    WA_WEBHOOK_VERIFY_TOKEN: str = "my-webhook-verify-token"
    WA_API_VERSION: str = "v19.0"

    # ── Telegram Bot ──────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = "tg-secret-token"

    # ── Facebook / Instagram ──────────────────────────────
    FB_PAGE_ID: str = ""
    FB_ACCESS_TOKEN: str = ""
    FB_APP_SECRET: str = ""

    # ── Email (SMTP) ──────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    # ── Agent behaviour ───────────────────────────────────
    AGENT_MAX_AUTO_QUOTE: float = 10_000
    AGENT_MAX_DISCOUNT_PCT: float = 10.0

    # ── CORS ─────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]

    model_config = {
        **({"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8"} if _ENV_FILE else {}),
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
