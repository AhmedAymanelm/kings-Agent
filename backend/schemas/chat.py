"""schemas/chat.py"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class MessageOut(BaseModel):
    id: int
    sender: str
    body: str
    created_at: datetime
    model_config = {"from_attributes": True}


class ChatOut(BaseModel):
    id: int
    customer_id: int
    channel: str
    ai_handling: bool
    unread_count: int
    last_message: str
    last_at: datetime
    messages: list[MessageOut] = []
    # Enriched fields joined from Customer
    customer_name:    Optional[str] = None
    customer_segment: Optional[str] = None
    model_config = {"from_attributes": True}


class SendMessageIn(BaseModel):
    text: str
