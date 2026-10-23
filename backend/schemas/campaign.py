"""schemas/campaign.py"""
from pydantic import BaseModel
from typing import Optional


class TemplateOut(BaseModel):
    id: int
    name: str
    category: str
    body: str
    status: str
    reject_reason: str
    model_config = {"from_attributes": True}


class TemplateIn(BaseModel):
    name: str
    category: str
    body: str


class CampaignOut(BaseModel):
    id: int
    name: str
    channel: str
    audience: str
    recipient_count: int
    status: str
    sent: int
    read: int
    replied: int
    scheduled_at: str
    model_config = {"from_attributes": True}
