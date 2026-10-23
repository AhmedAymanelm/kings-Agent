"""schemas/approval.py"""
from pydantic import BaseModel
from typing import Optional


class ApprovalOut(BaseModel):
    id: int
    type: str
    customer: str
    requested_by: str
    reason: str
    body_text: str
    status: str
    decided_at: str
    model_config = {"from_attributes": True}


class ApprovalDecision(BaseModel):
    text: Optional[str] = None   # edited text before approving
