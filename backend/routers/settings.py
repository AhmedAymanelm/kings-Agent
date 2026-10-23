"""
routers/settings.py — Agent settings, knowledge base, and connections
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.knowledge import KnowledgeEntry
from ..models.settings import AgentSettings
from ..schemas.knowledge import KBEntryOut, KBEntryIn
from ..schemas.settings import AgentSettingsOut, AgentSettingsPatch

router = APIRouter(prefix="/settings", tags=["settings"])


# ── Knowledge base ─────────────────────────────────────
@router.get("/kb", response_model=list[KBEntryOut])
def list_kb(db: Session = Depends(get_db)):
    return db.query(KnowledgeEntry).order_by(KnowledgeEntry.id.desc()).all()


@router.post("/kb", response_model=KBEntryOut, status_code=201)
def add_kb(body: KBEntryIn, db: Session = Depends(get_db)):
    entry = KnowledgeEntry(category=body.category, question=body.question, answer=body.answer)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/kb/{entry_id}", status_code=204)
def delete_kb(entry_id: int, db: Session = Depends(get_db)):
    e = db.get(KnowledgeEntry, entry_id)
    if not e:
        raise HTTPException(404, "Not found")
    db.delete(e)
    db.commit()


# ── Agent settings ─────────────────────────────────────
def _get_or_create_settings(db: Session) -> AgentSettings:
    s = db.get(AgentSettings, 1)
    if not s:
        s = AgentSettings(id=1)
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


@router.get("/agent", response_model=AgentSettingsOut)
def get_agent_settings(db: Session = Depends(get_db)):
    return _get_or_create_settings(db)


@router.put("/agent", response_model=AgentSettingsOut)
def update_agent_settings(patch: AgentSettingsPatch, db: Session = Depends(get_db)):
    s = _get_or_create_settings(db)
    for field, val in patch.model_dump(exclude_none=True).items():
        setattr(s, field, val)
    db.commit()
    db.refresh(s)
    return s


# ── Connections (placeholder — real integration in services/) ──
@router.put("/connections/{key}")
def toggle_connection(key: str, db: Session = Depends(get_db)):
    return {"key": key, "status": "toggled (demo)"}


@router.post("/connections/xls/sync")
def sync_xls():
    return {"sync": "now"}
