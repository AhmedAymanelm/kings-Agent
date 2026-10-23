"""schemas/project.py"""
from pydantic import BaseModel


class ProjectOut(BaseModel):
    id: int
    name: str
    customer: str
    stage: int
    progress: int
    due_note: str
    reminder: str
    is_late: bool
    model_config = {"from_attributes": True}
