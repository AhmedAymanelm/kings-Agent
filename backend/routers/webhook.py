"""
routers/webhook.py — WhatsApp incoming webhook endpoint

Flow:
  1. GET  /webhook  → verification handshake with Meta
  2. POST /webhook  → receive messages → AI agent processes → auto-reply or escalate
"""
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import whatsapp as wa_service
from ..config import settings
# AI agent imported lazily to avoid circular import
import importlib

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.get("")
def verify_webhook(request: Request):
    """Meta webhook verification handshake."""
    params     = request.query_params
    mode       = params.get("hub.mode")
    token      = params.get("hub.verify_token")
    challenge  = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WA_WEBHOOK_VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")

    raise HTTPException(403, "Forbidden")


@router.post("")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receive WhatsApp message events.
    Hands off to the AI agent for processing.
    """
    payload = await request.json()

    # Extract messages from WhatsApp payload format
    messages = wa_service.parse_webhook(payload)

    for msg in messages:
        if not msg["text"]:
            continue  # Skip non-text (images, voice, etc.) for now

        # Mark as read immediately
        if msg["wa_msg_id"]:
            try:
                await wa_service.mark_as_read(msg["wa_msg_id"])
            except Exception:
                pass

        # Hand to AI agent
        try:
            agent_mod = importlib.import_module("ai.agent")
            await agent_mod.handle_incoming(
                phone      = msg["phone"],
                text       = msg["text"],
                wa_msg_id  = msg["wa_msg_id"],
                db         = db,
            )
        except Exception as e:
            print(f"[webhook] Agent error: {e}")

    # WhatsApp requires a 200 response quickly
    return {"status": "ok"}


@router.post("/agent/toggle")
async def toggle_agent(body: dict, db: Session = Depends(get_db)):
    """Enable or disable the AI agent globally."""
    from ..models.settings import AgentSettings
    s = db.get(AgentSettings, 1)
    if s:
        s.is_active = body.get("active", True)
        db.commit()
    return {"active": body.get("active", True)}


@router.get("/insights/recommendations")
def get_recommendations():
    """Placeholder — AI-generated recommendations."""
    return [
        {"id": 0, "k": "high", "t": "6 عملاء مهتمين لم يردوا منذ 3 أيام",
         "d": "أجهّز رسالة متابعة مخصصة لكل عميل.", "a": "جهّز المتابعة"},
    ]


@router.post("/insights/recommendations/{rec_id}/apply")
def apply_recommendation(rec_id: int):
    return {"ok": True, "id": rec_id}
