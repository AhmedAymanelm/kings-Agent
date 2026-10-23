"""schemas/settings.py"""
from pydantic import BaseModel
from typing import Optional


class AgentSettingsOut(BaseModel):
    name: str
    tone: str
    language: str
    greeting: str
    work_days: str
    work_from: str
    work_to: str
    off_msg: str
    hand_angry: bool
    hand_discount: bool
    hand_amount: bool
    hand_call: bool
    hand_unknown: bool
    approval_limit: float
    max_discount: float
    is_active: bool
    model_config = {"from_attributes": True}


class AgentSettingsPatch(BaseModel):
    name: Optional[str] = None
    tone: Optional[str] = None
    language: Optional[str] = None
    greeting: Optional[str] = None
    work_days: Optional[str] = None
    work_from: Optional[str] = None
    work_to: Optional[str] = None
    off_msg: Optional[str] = None
    hand_angry: Optional[bool] = None
    hand_discount: Optional[bool] = None
    hand_amount: Optional[bool] = None
    hand_call: Optional[bool] = None
    hand_unknown: Optional[bool] = None
    approval_limit: Optional[float] = None
    max_discount: Optional[float] = None
    is_active: Optional[bool] = None
