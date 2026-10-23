"""schemas/knowledge.py"""
from pydantic import BaseModel


class KBEntryOut(BaseModel):
    id: int
    category: str
    question: str
    answer: str
    model_config = {"from_attributes": True}


class KBEntryIn(BaseModel):
    category: str
    question: str
    answer: str
