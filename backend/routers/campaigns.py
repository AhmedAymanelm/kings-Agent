"""
routers/campaigns.py — Campaigns and WhatsApp templates
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.campaign import Campaign, Template
from ..schemas.campaign import CampaignOut, TemplateOut, TemplateIn

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/", response_model=list[CampaignOut])
def list_campaigns(db: Session = Depends(get_db)):
    return db.query(Campaign).order_by(Campaign.id.desc()).all()


@router.get("/templates", response_model=list[TemplateOut])
def list_templates(db: Session = Depends(get_db)):
    return db.query(Template).order_by(Template.id.desc()).all()


@router.post("/templates", response_model=TemplateOut, status_code=201)
def create_template(body: TemplateIn, db: Session = Depends(get_db)):
    tpl = Template(name=body.name, category=body.category, body=body.body, status="review")
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    # TODO: Submit to WhatsApp Business API for review
    return tpl


@router.put("/templates/{tpl_id}/approve", response_model=TemplateOut)
def approve_template(tpl_id: int, db: Session = Depends(get_db)):
    """Simulate Meta approval (demo only — real approval comes from webhook)."""
    t = db.get(Template, tpl_id)
    if not t:
        raise HTTPException(404, "Template not found")
    t.status = "approved"
    db.commit()
    db.refresh(t)
    return t
