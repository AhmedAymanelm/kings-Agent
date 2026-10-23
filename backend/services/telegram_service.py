from __future__ import annotations
"""
services/telegram_service.py — Telegram Bot API integration

Uses the Telegram Bot API directly via httpx (no extra library needed).

Handles:
- Sending text messages to users
- Sending formatted HTML messages
- Sending inline keyboard buttons
- Parsing incoming webhook updates
- Setting the webhook URL
"""
from typing import Optional
import httpx
from ..config import settings

TG_BASE = "https://api.telegram.org/bot"


def _tg_configured() -> bool:
    return bool(settings.TELEGRAM_BOT_TOKEN)


def _url(method: str) -> str:
    return f"{TG_BASE}{settings.TELEGRAM_BOT_TOKEN}/{method}"


# ── Core send functions ────────────────────────────────────────────────────

async def send_message(chat_id: object, text: str,
                       parse_mode: str = "HTML",
                       reply_markup: Optional[dict] = None) -> dict:
    """
    Send a text message to a Telegram user.
    Supports HTML formatting: <b>bold</b>, <i>italic</i>, <code>code</code>
    """
    if not _tg_configured():
        return {"ok": False, "description": "Telegram not configured"}

    payload: dict = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(_url("sendMessage"), json=payload)
        return resp.json()


async def send_typing(chat_id: object) -> None:
    """Show 'typing...' indicator in the chat."""
    if not _tg_configured():
        return
    async with httpx.AsyncClient(timeout=5) as client:
        await client.post(_url("sendChatAction"), json={
            "chat_id": chat_id, "action": "typing"
        })


async def send_quick_replies(chat_id: object, text: str,
                              buttons: list[str]) -> dict:
    """Send a message with quick-reply keyboard buttons."""
    keyboard = {
        "keyboard": [[{"text": b}] for b in buttons],
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }
    return await send_message(chat_id, text, reply_markup=keyboard)


async def send_inline_buttons(chat_id: object, text: str,
                               buttons: list[dict]) -> dict:
    """
    Send a message with inline buttons.
    buttons: [{"text": "Label", "callback_data": "action_key"}, ...]
    """
    markup = {"inline_keyboard": [buttons]}
    return await send_message(chat_id, text, reply_markup=markup)


async def answer_callback(callback_query_id: str, text: str = "") -> dict:
    """Answer a callback query (removes the loading spinner)."""
    if not _tg_configured():
        return {}
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.post(_url("answerCallbackQuery"), json={
            "callback_query_id": callback_query_id,
            "text": text,
        })
        return resp.json()


# ── Webhook management ─────────────────────────────────────────────────────

async def set_webhook(webhook_url: str) -> dict:
    """
    Register the webhook URL with Telegram.
    Call once after deployment:
      await telegram_service.set_webhook("https://yourdomain.com/api/v1/telegram/webhook")
    """
    if not _tg_configured():
        return {"ok": False, "description": "Bot token not set"}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(_url("setWebhook"), json={
            "url": webhook_url,
            "secret_token": settings.TELEGRAM_WEBHOOK_SECRET,
            "allowed_updates": ["message", "callback_query"],
        })
        return resp.json()


async def delete_webhook() -> dict:
    if not _tg_configured():
        return {}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(_url("deleteWebhook"))
        return resp.json()


async def get_webhook_info() -> dict:
    if not _tg_configured():
        return {}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(_url("getWebhookInfo"))
        return resp.json()


# ── Update parsing ─────────────────────────────────────────────────────────

def parse_update(payload: dict) -> Optional[dict]:
    """
    Extract structured data from a Telegram Update object.
    Returns:
      {
        "type":        "message" | "callback",
        "chat_id":     int,
        "user_id":     int,
        "username":    str,
        "first_name":  str,
        "text":        str,           # message text or callback data
        "message_id":  int,
        "update_id":   int,
      }
    Returns None if the update type is not supported.
    """
    update_id = payload.get("update_id", 0)

    # ── Normal text message ──
    if "message" in payload:
        msg  = payload["message"]
        user = msg.get("from", {})
        return {
            "type":       "message",
            "chat_id":    msg["chat"]["id"],
            "user_id":    user.get("id"),
            "username":   user.get("username", ""),
            "first_name": user.get("first_name", ""),
            "text":       msg.get("text", ""),
            "message_id": msg.get("message_id", 0),
            "update_id":  update_id,
        }

    # ── Inline button press ──
    if "callback_query" in payload:
        cq   = payload["callback_query"]
        user = cq.get("from", {})
        return {
            "type":       "callback",
            "chat_id":    cq["message"]["chat"]["id"],
            "user_id":    user.get("id"),
            "username":   user.get("username", ""),
            "first_name": user.get("first_name", ""),
            "text":       cq.get("data", ""),
            "message_id": cq["message"].get("message_id", 0),
            "update_id":  update_id,
            "callback_id": cq.get("id", ""),
        }

    return None
