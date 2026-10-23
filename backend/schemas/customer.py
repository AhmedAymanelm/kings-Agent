"""schemas/customer.py"""
from pydantic import BaseModel
from typing import Optional


class CustomerOut(BaseModel):
    id: int
    name: str
    phone: str
    source: str
    segment: str
    value: float
    project: str
    consent: str
    consent_date: str
    consent_src: str
    last_contact: str
    model_config = {"from_attributes": True}


class CustomerPatch(BaseModel):
    segment: Optional[str] = None
    value: Optional[float] = None
    project: Optional[str] = None
    consent: Optional[str] = None
    consent_date: Optional[str] = None
    consent_src: Optional[str] = None
    last_contact: Optional[str] = None
    notes: Optional[str] = None
