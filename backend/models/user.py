"""models/user.py — System users (manager / staff)"""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id:         Mapped[int]      = mapped_column(primary_key=True, index=True)
    email:      Mapped[str]      = mapped_column(String(255), unique=True, index=True, nullable=False)
    name:       Mapped[str]      = mapped_column(String(120), nullable=False)
    role:       Mapped[str]      = mapped_column(String(20), nullable=False)   # 'manager' | 'staff'
    hashed_pw:  Mapped[str]      = mapped_column(String(255), nullable=False)
    is_active:  Mapped[bool]     = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
