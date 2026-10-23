"""models/customer.py — CRM customers"""
from datetime import datetime
from sqlalchemy import String, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class Customer(Base):
    __tablename__ = "customers"

    id:         Mapped[int]        = mapped_column(primary_key=True, index=True)
    name:       Mapped[str]        = mapped_column(String(200), nullable=False)
    phone:      Mapped[str]        = mapped_column(String(30),  nullable=False, index=True)
    source:     Mapped[str]        = mapped_column(String(80),  default="")      # واتساب / إعلان / موقع
    segment:    Mapped[str]        = mapped_column(String(20),  default="new")   # new/interested/ready/current/idle
    value:      Mapped[float]      = mapped_column(Float,        default=0.0)    # deal value EGP
    project:    Mapped[str]        = mapped_column(String(200),  default="—")
    consent:    Mapped[str]        = mapped_column(String(10),   default="none") # in/out/none
    consent_date: Mapped[str]      = mapped_column(String(50),   default="—")
    consent_src:  Mapped[str]      = mapped_column(String(100),  default="—")
    last_contact: Mapped[str]      = mapped_column(String(80),   default="")
    notes:      Mapped[str]        = mapped_column(String(1000), default="")
    created_at: Mapped[datetime]   = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime]   = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
