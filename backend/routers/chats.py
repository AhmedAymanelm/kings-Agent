"""
routers/chats.py — Conversation and message endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.chat import Chat, Message
from ..models.customer import Customer
from ..schemas.chat import ChatOut, SendMessageIn, MessageOut
from ..services import whatsapp as wa_service

router = APIRouter(prefix="/chats", tags=["chats"])


def _enrich(chat: Chat, db: Session) -> dict:
    """Add customer_name and customer_segment to a Chat ORM object as extra attrs."""
    cust: Optional[Customer] = db.get(Customer, chat.customer_id)
    # Attach virtual attrs so Pydantic can read them via model_validate
    chat.customer_name    = cust.name    if cust else "عميل"
    chat.customer_segment = cust.segment if cust else "new"
    return chat


@router.get("/", response_model=list[ChatOut])
def list_chats(db: Session = Depends(get_db)):
    chats = db.query(Chat).order_by(Chat.last_at.desc()).all()
    return [_enrich(c, db) for c in chats]


@router.get("/{chat_id}", response_model=ChatOut)
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found")
    # Mark as read
    chat.unread_count = 0
    db.commit()
    return _enrich(chat, db)


@router.post("/{chat_id}/messages", response_model=MessageOut)
async def send_message(chat_id: int, body: SendMessageIn,
                       db: Session = Depends(get_db)):
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found")

    msg = Message(chat_id=chat_id, sender="human", body=body.text)
    db.add(msg)
    chat.last_message = body.text
    chat.ai_handling  = False
    db.commit()
    db.refresh(msg)

    # Forward to the right channel
    try:
        if chat.channel == "telegram":
            from ..services import telegram_service as tg
            cust = db.get(Customer, chat.customer_id)
            if cust and cust.phone.startswith("TG:"):
                tg_id = cust.phone[3:]
                await tg.send_message(tg_id, body.text)
        else:
            await wa_service.send_text(chat.customer_id, body.text, db)
    except Exception as e:
        print(f"[send_message] forward error: {e}")

    return msg
