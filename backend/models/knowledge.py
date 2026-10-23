"""models/knowledge.py — Agent knowledge base entries"""
from datetime import datetime
from sqlalchemy import String, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class KnowledgeEntry(Base):
    __tablename__ = "knowledge"

    id:         Mapped[int]      = mapped_column(primary_key=True, index=True)
    category:   Mapped[str]      = mapped_column(String(50), nullable=False)
    question:   Mapped[str]      = mapped_column(String(500), nullable=False)
    answer:     Mapped[str]      = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
