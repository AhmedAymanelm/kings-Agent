"""models/campaign.py — Marketing campaigns and WhatsApp templates"""
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class Template(Base):
    __tablename__ = "templates"

    id:         Mapped[int]      = mapped_column(primary_key=True, index=True)
    name:       Mapped[str]      = mapped_column(String(200), nullable=False)
    category:   Mapped[str]      = mapped_column(String(50),  default="تسويقية")
    body:       Mapped[str]      = mapped_column(Text, nullable=False)
    status:     Mapped[str]      = mapped_column(String(20),  default="review")   # approved/review/rejected
    reject_reason: Mapped[str]   = mapped_column(String(500), default="")
    wa_template_id: Mapped[str]  = mapped_column(String(100), default="")         # Meta template ID
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Campaign(Base):
    __tablename__ = "campaigns"

    id:          Mapped[int]      = mapped_column(primary_key=True, index=True)
    name:        Mapped[str]      = mapped_column(String(200), nullable=False)
    channel:     Mapped[str]      = mapped_column(String(50),  default="whatsapp")
    audience:    Mapped[str]      = mapped_column(String(200), default="")
    recipient_count: Mapped[int]  = mapped_column(Integer, default=0)
    status:      Mapped[str]      = mapped_column(String(20),  default="draft")   # draft/scheduled/running/done
    template_id: Mapped[int]      = mapped_column(default=0)
    sent:        Mapped[int]      = mapped_column(Integer, default=0)
    read:        Mapped[int]      = mapped_column(Integer, default=0)
    replied:     Mapped[int]      = mapped_column(Integer, default=0)
    scheduled_at: Mapped[str]     = mapped_column(String(100), default="")
    created_at:  Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
