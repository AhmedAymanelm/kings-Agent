"""models/chat.py — Conversations and individual messages"""
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Chat(Base):
    __tablename__ = "chats"

    id:           Mapped[int]      = mapped_column(primary_key=True, index=True)
    customer_id:  Mapped[int]      = mapped_column(ForeignKey("customers.id"), index=True)
    channel:      Mapped[str]      = mapped_column(String(20), default="whatsapp")  # whatsapp | email
    ai_handling:  Mapped[bool]     = mapped_column(Boolean, default=True)
    unread_count: Mapped[int]      = mapped_column(default=0)
    last_message: Mapped[str]      = mapped_column(String(500), default="")
    last_at:      Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_at:   Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="chat",
                                                      order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id:          Mapped[int]      = mapped_column(primary_key=True, index=True)
    chat_id:     Mapped[int]      = mapped_column(ForeignKey("chats.id"), index=True)
    sender:      Mapped[str]      = mapped_column(String(10))  # 'customer' | 'ai' | 'human'
    body:        Mapped[str]      = mapped_column(Text, nullable=False)
    wa_msg_id:   Mapped[str]      = mapped_column(String(100), default="", index=True)  # WhatsApp message ID
    created_at:  Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
