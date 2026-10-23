"""models/settings.py — Persisted agent settings (single-row table)"""
from sqlalchemy import String, Boolean, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class AgentSettings(Base):
    __tablename__ = "agent_settings"

    id:          Mapped[int]   = mapped_column(primary_key=True, default=1)
    name:        Mapped[str]   = mapped_column(String(100), default="مساعد")
    tone:        Mapped[str]   = mapped_column(String(50),  default="ودود ومحترف")
    language:    Mapped[str]   = mapped_column(String(50),  default="عامية مصرية")
    greeting:    Mapped[str]   = mapped_column(Text, default="أهلاً بحضرتك!")
    work_days:   Mapped[str]   = mapped_column(String(20),  default="0111110")  # 7-char bitmask (Sat→Fri)
    work_from:   Mapped[str]   = mapped_column(String(5),   default="09:00")
    work_to:     Mapped[str]   = mapped_column(String(5),   default="18:00")
    off_msg:     Mapped[str]   = mapped_column(Text, default="نحن خارج أوقات العمل.")
    # Handoff rules
    hand_angry:   Mapped[bool] = mapped_column(Boolean, default=True)
    hand_discount: Mapped[bool]= mapped_column(Boolean, default=True)
    hand_amount:  Mapped[bool] = mapped_column(Boolean, default=True)
    hand_call:    Mapped[bool] = mapped_column(Boolean, default=True)
    hand_unknown: Mapped[bool] = mapped_column(Boolean, default=True)
    approval_limit: Mapped[float] = mapped_column(Float, default=10000.0)
    max_discount:   Mapped[float] = mapped_column(Float, default=10.0)
    # Agent on/off
    is_active:   Mapped[bool]  = mapped_column(Boolean, default=True)
