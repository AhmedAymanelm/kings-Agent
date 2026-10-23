"""
ai/agent.py — Core AI agent logic

Entry point: handle_incoming()

Flow for each incoming WhatsApp message:
  1. Find or create customer + chat in DB
  2. Load agent settings & KB
  3. Classify intent
  4. Decide: auto-reply | escalate to human | request approval
  5. Send reply (or create approval record)
"""
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from .llm import chat_complete
from .prompts import SYSTEM_PROMPT, CLASSIFY_PROMPT, SUGGEST_REPLY_PROMPT
from .knowledge_base import load_kb_text

from backend.models.customer import Customer
from backend.models.chat import Chat, Message
from backend.models.approval import Approval
from backend.models.settings import AgentSettings
from backend.services import whatsapp as wa_service
from backend.config import settings as cfg


# ── Constants ─────────────────────────────────────────────────────────────

# Intents that always require a human
HUMAN_ESCALATION_INTENTS = {"complaint", "call_request"}

# Keywords that trigger instant opt-out
OPT_OUT_KEYWORDS = {"إيقاف", "stop", "unsubscribe", "إلغاء", "لا أريد"}


# ── Main entry point ──────────────────────────────────────────────────────

async def handle_incoming(phone: str, text: str, wa_msg_id: str, db: Session) -> None:
    """
    Process one incoming WhatsApp message end-to-end.
    Called from the WhatsApp webhook router.
    """
    agent_cfg = db.get(AgentSettings, 1)
    if not agent_cfg or not agent_cfg.is_active:
        return

    if _is_opt_out(text):
        await _handle_opt_out(phone, db)
        return

    if not _in_working_hours(agent_cfg):
        await wa_service.send_text_by_phone(phone, agent_cfg.off_msg)
        return

    customer = _find_or_create_customer(phone, db)
    chat     = _find_or_create_chat(customer.id, db)

    msg = Message(chat_id=chat.id, sender="customer", body=text, wa_msg_id=wa_msg_id)
    db.add(msg)
    chat.last_message = text
    chat.last_at      = datetime.utcnow()
    db.commit()

    intent = await _classify_intent(text)

    if intent in HUMAN_ESCALATION_INTENTS:
        await _escalate_to_human(chat, customer, text, intent, agent_cfg, db)
        return

    if intent == "discount":
        await _handle_discount_request(chat, customer, text, agent_cfg, db)
        return

    kb_text  = load_kb_text(db)
    history  = _build_history(chat, db)
    system   = _build_system_prompt(agent_cfg, kb_text)
    messages = [{"role": "system", "content": system}] + history

    reply = await chat_complete(messages)
    if not reply:
        reply = "شكراً لتواصلك، سنرد عليك في أقرب وقت."

    await _send_and_save(chat, reply, db)


async def handle_incoming_tg(tg_chat_id: int, text: str,
                              customer, chat, db: Session) -> None:
    """
    Process one incoming Telegram message end-to-end.
    Called from the Telegram webhook router.
    """
    from backend.services import telegram_service as tg_svc

    agent_cfg = db.get(AgentSettings, 1)
    if not agent_cfg or not agent_cfg.is_active:
        await tg_svc.send_message(tg_chat_id,
            "الوكيل متوقف مؤقتاً. تواصل معنا مباشرة على واتساب.")
        return

    if not _in_working_hours(agent_cfg):
        await tg_svc.send_message(tg_chat_id, agent_cfg.off_msg)
        return

    if _is_opt_out(text):
        if customer:
            customer.consent = "out"
            db.commit()
        await tg_svc.send_message(tg_chat_id,
            "تم إلغاء اشتراكك ✅. لن تصلك رسائل منا.")
        return

    intent = await _classify_intent(text)

    if intent in HUMAN_ESCALATION_INTENTS:
        chat.ai_handling  = False
        chat.unread_count += 1
        db.commit()
        holding = {
            "complaint":    "فهمت موقفك تماماً. سيتواصل معك أحد من فريقنا قريباً. 🙏",
            "call_request": "حسناً! سيتواصل معك أحد من فريقنا خلال وقت قصير. 📞",
        }.get(intent, "سيتواصل معك أحد من فريقنا قريباً.")
        reply_msg = Message(chat_id=chat.id, sender="ai", body=holding)
        db.add(reply_msg)
        db.commit()
        await tg_svc.send_message(tg_chat_id, holding)
        return

    if intent == "discount":
        max_disc   = agent_cfg.max_discount if agent_cfg else 10.0
        auto_reply = (f"يسعدنا مساعدتك! أقصى خصم يمكنني تقديمه هو <b>{max_disc:.0f}%</b>. "
                      f"لو محتاج أكثر، سأرفع الطلب للمدير.")
        msg_db = Message(chat_id=chat.id, sender="ai", body=auto_reply)
        db.add(msg_db)
        db.commit()
        await tg_svc.send_message(tg_chat_id, auto_reply)
        return

    # Generate AI reply
    kb_text  = load_kb_text(db)
    history  = _build_history(chat, db)
    system   = _build_system_prompt(agent_cfg, kb_text)
    messages = [{"role": "system", "content": system}] + history
    messages.append({"role": "user", "content": text})

    reply = await chat_complete(messages)
    if not reply:
        reply = "شكراً لتواصلك، سنرد عليك في أقرب وقت. 🙏"

    # Save to DB
    reply_msg = Message(chat_id=chat.id, sender="ai", body=reply)
    db.add(reply_msg)
    chat.last_message = reply
    chat.last_at      = datetime.utcnow()
    db.commit()

    # Send via Telegram
    await tg_svc.send_message(tg_chat_id, reply)



# ── Intent classification ─────────────────────────────────────────────────

async def _classify_intent(text: str) -> str:
    prompt = CLASSIFY_PROMPT.format(message=text)
    result = await chat_complete([{"role": "user", "content": prompt}], max_tokens=10)
    return result.strip().lower().split()[0] if result.strip() else "inquiry"


# ── Suggested reply for human agents ─────────────────────────────────────

async def suggest_reply(chat_id: int, db: Session) -> str:
    """Generate a suggested reply for human agents in the dashboard."""
    chat    = db.get(Chat, chat_id)
    if not chat:
        return ""
    agent_cfg = db.get(AgentSettings, 1)
    tone      = agent_cfg.tone if agent_cfg else "ودود ومحترف"
    history   = _format_history_text(chat, db)
    prompt    = SUGGEST_REPLY_PROMPT.format(tone=tone, conversation=history)
    return await chat_complete([{"role": "user", "content": prompt}])


# ── Escalation helpers ────────────────────────────────────────────────────

async def _escalate_to_human(chat, customer, text, intent, agent_cfg, db):
    """Mark chat as needing human, notify agent, send holding message."""
    chat.ai_handling  = False
    chat.unread_count += 1
    db.commit()

    holding = {
        "complaint":    "فهمت موقفك تماماً، وسيتواصل معك أحد من فريقنا في أقرب وقت.",
        "call_request": "حسناً! سيتصل بك أحد من فريقنا خلال وقت قصير.",
    }.get(intent, "سيتواصل معك أحد من فريقنا قريباً.")

    await _send_and_save(chat, holding, db)


async def _handle_discount_request(chat, customer, text, agent_cfg, db):
    """Create an approval request for a discount above the agent's limit."""
    max_disc = agent_cfg.max_discount if agent_cfg else cfg.AGENT_MAX_DISCOUNT_PCT

    # First reply with the max auto-discount
    auto_reply = f"يسعدنا مساعدتك! أقصى خصم يمكنني تقديمه مباشرةً هو {max_disc:.0f}%. لو محتاج أكثر، سأرفع الطلب للمدير."
    await _send_and_save(chat, auto_reply, db)

    # Create approval record
    a = Approval(
        type="طلب خصم",
        customer=customer.name,
        customer_id=customer.id,
        requested_by="الوكيل",
        reason=f"العميل طلب خصماً أكبر من {max_disc}%",
        body_text=f"العميل {customer.name} طلب خصماً. الرسالة: {text}",
        status="pending",
    )
    db.add(a)
    db.commit()


async def _handle_opt_out(phone: str, db: Session) -> None:
    """Mark customer as opted-out."""
    customer = db.query(Customer).filter(Customer.phone.contains(phone[-9:])).first()
    if customer:
        customer.consent     = "out"
        customer.consent_date = datetime.utcnow().strftime("%Y-%m-%d")
        customer.consent_src  = 'رد "إيقاف"'
        db.commit()
    # Send confirmation
    await wa_service.send_text_by_phone(
        phone, "تم إلغاء اشتراكك. لن تصلك رسائل منا. للعودة، راسلنا في أي وقت."
    )


# ── DB helpers ────────────────────────────────────────────────────────────

def _find_or_create_customer(phone: str, db: Session) -> Customer:
    # Match on last 9 digits to handle prefix variations
    tail = phone[-9:]
    customer = db.query(Customer).filter(Customer.phone.contains(tail)).first()
    if not customer:
        customer = Customer(
            name=f"عميل {phone[-4:]}",
            phone=phone,
            source="واتساب",
            segment="new",
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    return customer


def _find_or_create_chat(customer_id: int, db: Session) -> Chat:
    chat = db.query(Chat).filter(
        Chat.customer_id == customer_id,
        Chat.channel == "whatsapp",
    ).first()
    if not chat:
        chat = Chat(customer_id=customer_id, channel="whatsapp", ai_handling=True)
        db.add(chat)
        db.commit()
        db.refresh(chat)
    return chat


# ── Prompt building ───────────────────────────────────────────────────────

def _build_system_prompt(agent_cfg: AgentSettings | None, kb_text: str) -> str:
    return SYSTEM_PROMPT.format(
        company_name   = agent_cfg.name    if agent_cfg else "الشركة",
        tone           = agent_cfg.tone    if agent_cfg else "ودود ومحترف",
        language       = agent_cfg.language if agent_cfg else "عامية مصرية",
        max_discount   = agent_cfg.max_discount if agent_cfg else 10,
        approval_limit = agent_cfg.approval_limit if agent_cfg else 10000,
        work_from      = agent_cfg.work_from if agent_cfg else "09:00",
        work_to        = agent_cfg.work_to   if agent_cfg else "18:00",
        work_days      = "الأحد – الخميس",
        off_msg        = agent_cfg.off_msg   if agent_cfg else "سنرد قريباً.",
        knowledge_base = kb_text,
    )


def _build_history(chat: Chat, db: Session) -> list[dict]:
    msgs = db.query(Message).filter(Message.chat_id == chat.id).order_by(Message.created_at).all()
    role_map = {"customer": "user", "ai": "assistant", "human": "assistant"}
    return [{"role": role_map.get(m.sender, "user"), "content": m.body} for m in msgs[-20:]]


def _format_history_text(chat: Chat, db: Session) -> str:
    msgs = db.query(Message).filter(Message.chat_id == chat.id).order_by(Message.created_at).all()
    lines = []
    for m in msgs[-10:]:
        label = {"customer": "العميل", "ai": "الوكيل", "human": "الموظف"}.get(m.sender, "")
        lines.append(f"{label}: {m.body}")
    return "\n".join(lines)


# ── Time check ────────────────────────────────────────────────────────────

def _in_working_hours(agent_cfg: AgentSettings | None) -> bool:
    if not agent_cfg:
        return True
    now    = datetime.now()
    weekday = now.weekday()  # 0=Monday
    # work_days is a 7-char bitmask: index 0=Saturday, … 6=Friday
    day_map = {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 0, 6: 1}  # Python weekday → bitmask index
    bitmask = agent_cfg.work_days
    if len(bitmask) == 7 and bitmask[day_map[weekday]] == "0":
        return False
    try:
        from_h, from_m = map(int, agent_cfg.work_from.split(":"))
        to_h, to_m     = map(int, agent_cfg.work_to.split(":"))
        now_minutes    = now.hour * 60 + now.minute
        return (from_h * 60 + from_m) <= now_minutes <= (to_h * 60 + to_m)
    except Exception:
        return True


def _is_opt_out(text: str) -> bool:
    return text.strip().lower() in {k.lower() for k in OPT_OUT_KEYWORDS}


# ── Send and persist ──────────────────────────────────────────────────────

async def _send_and_save(chat: Chat, reply: str, db: Session) -> None:
    """Save AI reply to DB and send via WhatsApp."""
    msg = Message(chat_id=chat.id, sender="ai", body=reply)
    db.add(msg)
    chat.last_message = reply
    chat.last_at      = datetime.utcnow()
    db.commit()

    try:
        await wa_service.send_text(chat.customer_id, reply, db)
    except Exception as e:
        print(f"[agent] Failed to send WA message: {e}")
