"""models/appointment.py — Scheduled appointments"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id:          Mapped[int]      = mapped_column(primary_key=True, index=True)
    day_label:   Mapped[str]      = mapped_column(String(100), nullable=False)  # e.g. "اليوم · الخميس 22 أكتوبر"
    time_label:  Mapped[str]      = mapped_column(String(20),  nullable=False)  # e.g. "1:30 م"
    title:       Mapped[str]      = mapped_column(String(200), nullable=False)
    customer:    Mapped[str]      = mapped_column(String(200), default="")
    customer_id: Mapped[int]      = mapped_column(default=0, index=True)
    channel:     Mapped[str]      = mapped_column(String(50),  default="واتساب")
    confirmed:   Mapped[bool]     = mapped_column(Boolean, default=False)
    created_at:  Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
