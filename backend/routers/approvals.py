from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.approval import Approval
from ..schemas.approval import ApprovalOut, ApprovalDecision

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/", response_model=list[ApprovalOut])
def list_approvals(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Approval)
    if status:
        q = q.filter(Approval.status == status)
    return q.order_by(Approval.created_at.desc()).all()


@router.post("/{approval_id}/approve", response_model=ApprovalOut)
def approve(approval_id: int, body: ApprovalDecision, db: Session = Depends(get_db)):
    a = db.get(Approval, approval_id)
    if not a:
        raise HTTPException(404, "Not found")
    if body.text:
        a.body_text = body.text
    a.status     = "approved"
    a.decided_at = "الآن"
    db.commit()
    db.refresh(a)
    return a


@router.post("/{approval_id}/reject", response_model=ApprovalOut)
def reject(approval_id: int, db: Session = Depends(get_db)):
    a = db.get(Approval, approval_id)
    if not a:
        raise HTTPException(404, "Not found")
    a.status     = "rejected"
    a.decided_at = "الآن"
    db.commit()
    db.refresh(a)
    return a
