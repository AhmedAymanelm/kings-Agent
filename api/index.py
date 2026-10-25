"""
api/index.py — Vercel Serverless Function entry point
"""
import sys
import traceback
from pathlib import Path

# Add project root to sys.path so 'backend' and 'ai' packages are importable
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

try:
    from backend.main import app
except Exception as exc:
    err_trace = traceback.format_exc()
    print("FATAL ERROR ON IMPORT backend.main:\n", err_trace)
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI()

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def fallback_error(full_path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Backend initialization failed",
                "detail": str(exc),
                "traceback": err_trace.splitlines(),
            },
        )
