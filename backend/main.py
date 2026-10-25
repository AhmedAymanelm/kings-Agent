"""
main.py — FastAPI application entry point

Local dev:
  uvicorn backend.main:app --reload --port 8000

Production (Railway):
  uvicorn backend.main:app --host 0.0.0.0 --port $PORT
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings
from .database import create_all_tables
from .routers import (
    auth, customers, chats, approvals,
    campaigns, projects, appointments,
    settings as settings_router,
    webhook, telegram_webhook,
)

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version="0.2.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    try:
        create_all_tables()
        print(f"✅ {settings.APP_NAME} started")
        print(f"   DB: {settings.DATABASE_URL[:40]}...")
        if settings.TELEGRAM_BOT_TOKEN:
            print(f"   🤖 Telegram: @{settings.TELEGRAM_BOT_USERNAME}")
    except Exception as e:
        print(f"⚠️ on_startup warning: {e}")


# ── API Routers (/api/v1) ──────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(auth.router,                  prefix=PREFIX)
app.include_router(customers.router,             prefix=PREFIX)
app.include_router(chats.router,                 prefix=PREFIX)
app.include_router(approvals.router,             prefix=PREFIX)
app.include_router(campaigns.router,             prefix=PREFIX)
app.include_router(projects.router,              prefix=PREFIX)
app.include_router(appointments.router,          prefix=PREFIX)
app.include_router(settings_router.router,       prefix=PREFIX)
app.include_router(webhook.router,               prefix=PREFIX)
app.include_router(telegram_webhook.router,      prefix=PREFIX)


# ── Health check ───────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}


# ── Serve frontend static files ────────────────────────────────────────────
_FRONTEND = Path(__file__).parent.parent / "frontend"

if _FRONTEND.exists() and (_FRONTEND / "css").is_dir() and (_FRONTEND / "js").is_dir():
    # Serve /css, /js, /assets etc.
    app.mount("/css",    StaticFiles(directory=_FRONTEND / "css"),    name="css")
    app.mount("/js",     StaticFiles(directory=_FRONTEND / "js"),     name="js")

    # Serve index.html for all non-API routes (SPA fallback)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        index = _FRONTEND / "index.html"
        return FileResponse(str(index))
