"""models/approval.py — Manager approval queue"""
from datetime import datetime
from sqlalchemy import String, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class Approval(Base):
    __tablename__ = "approvals"

    id:          Mapped[int]      = mapped_column(primary_key=True, index=True)
    type:        Mapped[str]      = mapped_column(String(50),  nullable=False)   # عرض سعر / طلب خصم / حملة / رد
    customer:    Mapped[str]      = mapped_column(String(200), default="")
    customer_id: Mapped[int]      = mapped_column(default=0, index=True)
    requested_by: Mapped[str]     = mapped_column(String(100), default="الوكيل")
    reason:      Mapped[str]      = mapped_column(String(500), nullable=False)
    body_text:   Mapped[str]      = mapped_column(Text, nullable=False)
    status:      Mapped[str]      = mapped_column(String(20),  default="pending")  # pending/approved/rejected
    decided_at:  Mapped[str]      = mapped_column(String(50),  default="")
    created_at:  Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
