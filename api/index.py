"""
api/index.py — Vercel entry point
Vercel looks for the ASGI app symbol here.
"""
import sys
from pathlib import Path

# Add project root to sys.path so 'backend' and 'ai' packages are importable
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.main import app  # noqa: F401 — ASGI app for Vercel
