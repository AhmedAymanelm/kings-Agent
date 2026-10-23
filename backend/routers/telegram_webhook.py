"""
routers/telegram_webhook.py — Telegram Bot webhook endpoints

Endpoints:
  POST /telegram/webhook          → receive Telegram updates
  POST /telegram/set-webhook      → register webhook URL with Telegram
  GET  /telegram/webhook-info     → check webhook status
  DELETE /telegram/webhook        → remove webhook (use polling instead)
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from ..services import telegram_service as tg
from ..models.customer import Customer
from ..models.chat import Chat, Message

router = APIRouter(prefix="/telegram", tags=["telegram"])

# ── Greeting flow ─────────────────────────────────────────────────────────
GREET_BUTTONS = ["💰 الأسعار", "📅 حجز موعد", "🤝 تواصل مع موظف", "❓ سؤال آخر"]


# ── Webhook receiver ──────────────────────────────────────────────────────
@router.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """Receive and process Telegram updates."""

    # Verify secret header (set when registering webhook)
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if secret != settings.TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(403, "Invalid secret")

    payload = await request.json()
    update  = tg.parse_update(payload)

    if not update:
        return {"ok": True}  # unsupported update type

    chat_id    = update["chat_id"]
    text       = update["text"].strip()
    first_name = update["first_name"] or update["username"] or f"TG-{chat_id}"

    # Answer callback queries immediately
    if update["type"] == "callback":
        await tg.answer_callback(update["callback_id"])

    # Find or create customer
    customer = _find_or_create_tg_customer(chat_id, first_name, db)
    chat     = _find_or_create_tg_chat(customer.id, chat_id, db)

    # Save incoming message
    msg = Message(chat_id=chat.id, sender="customer", body=text)
    db.add(msg)
    chat.last_message = text
    db.commit()

    # Handle /start command
    if text.lower() in ("/start", "start"):
        await tg.send_quick_replies(
            chat_id,
            f"أهلاً {first_name}! 👋\nأنا المساعد الذكي. كيف أساعدك اليوم؟",
            GREET_BUTTONS,
        )
        return {"ok": True}

    # Hand off to AI agent
    try:
        import importlib
        agent_mod = importlib.import_module("ai.agent")
        await agent_mod.handle_incoming_tg(
            tg_chat_id=chat_id,
            text=text,
            customer=customer,
            chat=chat,
            db=db,
        )
    except Exception as e:
        print(f"[tg_webhook] Agent error: {e}")
        await tg.send_message(chat_id, "شكراً لرسالتك! سنرد عليك قريباً. 🙏")

    return {"ok": True}


# ── Webhook management ────────────────────────────────────────────────────
@router.post("/set-webhook")
async def set_webhook(body: dict):
    """
    Register a webhook URL with Telegram.
    Body: {"url": "https://yourdomain.com"}
    """
    base_url = body.get("url", "").rstrip("/")
    if not base_url:
        raise HTTPException(400, "url is required")

    webhook_url = f"{base_url}/api/v1/telegram/webhook"
    result = await tg.set_webhook(webhook_url)
    return result


@router.get("/webhook-info")
async def webhook_info():
    """Get current webhook status from Telegram."""
    return await tg.get_webhook_info()


@router.delete("/webhook")
async def remove_webhook():
    """Remove webhook (switch to polling mode)."""
    return await tg.delete_webhook()


# ── DB helpers ────────────────────────────────────────────────────────────
def _find_or_create_tg_customer(tg_chat_id: object, name: str, db: Session) -> Customer:
    tg_id_str = f"TG:{tg_chat_id}"
    customer = db.query(Customer).filter(Customer.phone == tg_id_str).first()
    if not customer:
        customer = Customer(
            name=name,
            phone=tg_id_str,
            source="تيليجرام",
            segment="new",
            consent="in",
            consent_src="Telegram /start",
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    return customer


def _find_or_create_tg_chat(customer_id: int, tg_chat_id: object, db: Session) -> Chat:
    chat = db.query(Chat).filter(
        Chat.customer_id == customer_id,
        Chat.channel == "telegram",
    ).first()
    if not chat:
        chat = Chat(customer_id=customer_id, channel="telegram", ai_handling=True)
        db.add(chat)
        db.commit()
        db.refresh(chat)
    return chat
