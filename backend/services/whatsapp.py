"""
services/whatsapp.py — WhatsApp Business API integration
"""
from typing import Optional
import httpx
from sqlalchemy.orm import Session
from ..config import settings
from ..models.customer import Customer

WA_BASE = f"https://graph.facebook.com/{settings.WA_API_VERSION}"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.WA_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def _wa_configured() -> bool:
    return bool(settings.WA_ACCESS_TOKEN and settings.WA_PHONE_NUMBER_ID)


def _phone_of_customer(customer_id: int, db: Session) -> Optional[str]:
    c = db.get(Customer, customer_id)
    if not c:
        return None
    digits = "".join(d for d in c.phone if d.isdigit())
    if digits.startswith("0"):
        digits = "2" + digits
    return digits


async def send_text(customer_id: int, text: str, db: Session) -> dict:
    """Send a free-form text message to a customer via WhatsApp."""
    if not _wa_configured():
        return {"status": "skipped", "reason": "WhatsApp not configured"}

    phone = _phone_of_customer(customer_id, db)
    if not phone:
        return {"status": "error", "reason": "customer not found"}

    return await send_text_by_phone(phone, text)


async def send_text_by_phone(phone: str, text: str) -> dict:
    """Send a text message directly to a phone number."""
    if not _wa_configured():
        return {"status": "skipped"}

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text},
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{WA_BASE}/{settings.WA_PHONE_NUMBER_ID}/messages",
            headers=_headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


async def send_template(
    customer_id: int,
    template_name: str,
    language_code: str = "ar",
    components: Optional[list] = None,
    db: Optional[Session] = None,
) -> dict:
    """Send an approved WhatsApp template message."""
    if not _wa_configured():
        return {"status": "skipped", "reason": "WhatsApp not configured"}

    phone = _phone_of_customer(customer_id, db)
    if not phone:
        return {"status": "error", "reason": "customer not found"}

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
            "components": components or [],
        },
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{WA_BASE}/{settings.WA_PHONE_NUMBER_ID}/messages",
            headers=_headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


async def mark_as_read(wa_message_id: str) -> dict:
    """Mark a received WhatsApp message as read."""
    if not _wa_configured():
        return {}

    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": wa_message_id,
    }

    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.post(
            f"{WA_BASE}/{settings.WA_PHONE_NUMBER_ID}/messages",
            headers=_headers(),
            json=payload,
        )
        return resp.json()


def parse_webhook(payload: dict) -> list:
    """Extract individual messages from a WhatsApp webhook payload."""
    results = []
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    results.append({
                        "phone":     msg.get("from", ""),
                        "wa_msg_id": msg.get("id", ""),
                        "text":      msg.get("text", {}).get("body", ""),
                        "type":      msg.get("type", "text"),
                        "timestamp": msg.get("timestamp", ""),
                    })
    except Exception:
        pass
    return results
