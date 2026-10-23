"""
ai/knowledge_base.py — Loads the knowledge base from the DB and formats it for prompts
"""
from sqlalchemy.orm import Session


def load_kb_text(db: Session) -> str:
    """
    Returns knowledge base as a formatted string for injection into the system prompt.
    Falls back to empty string if DB unavailable.
    """
    try:
        from backend.models.knowledge import KnowledgeEntry
        entries = db.query(KnowledgeEntry).order_by(KnowledgeEntry.category).all()
        if not entries:
            return "لا توجد معلومات مضافة بعد."
        lines = []
        current_cat = None
        for e in entries:
            if e.category != current_cat:
                current_cat = e.category
                lines.append(f"\n[{current_cat}]")
            lines.append(f"  س: {e.question}")
            lines.append(f"  ج: {e.answer}")
        return "\n".join(lines)
    except Exception:
        return ""


def search_kb(db: Session, query: str) -> str:
    """
    Simple keyword search in the KB — returns best matching answers.
    In production, replace with vector similarity search.
    """
    try:
        from backend.models.knowledge import KnowledgeEntry
        entries = db.query(KnowledgeEntry).all()
        query_lower = query.lower()
        matches = [
            e for e in entries
            if query_lower in e.question.lower() or query_lower in e.answer.lower()
        ]
        if not matches:
            return ""
        return "\n".join(f"س: {e.question}\nج: {e.answer}" for e in matches[:3])
    except Exception:
        return ""
