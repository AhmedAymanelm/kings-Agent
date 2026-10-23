"""models/project.py — Projects / delivery pipeline"""
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class Project(Base):
    __tablename__ = "projects"

    id:          Mapped[int]      = mapped_column(primary_key=True, index=True)
    name:        Mapped[str]      = mapped_column(String(200), nullable=False)
    customer:    Mapped[str]      = mapped_column(String(200), default="")
    customer_id: Mapped[int]      = mapped_column(default=0, index=True)
    stage:       Mapped[int]      = mapped_column(Integer, default=0)   # 0=inquiry 1=quote 2=executing 3=delivered
    progress:    Mapped[int]      = mapped_column(Integer, default=0)   # 0-100 %
    due_note:    Mapped[str]      = mapped_column(String(200), default="")
    reminder:    Mapped[str]      = mapped_column(String(500), default="")
    is_late:     Mapped[bool]     = mapped_column(Boolean, default=False)
    created_at:  Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at:  Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
