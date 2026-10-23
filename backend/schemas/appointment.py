"""schemas/appointment.py"""
from pydantic import BaseModel


class AppointmentOut(BaseModel):
    id: int
    day_label: str
    time_label: str
    title: str
    customer: str
    channel: str
    confirmed: bool
    model_config = {"from_attributes": True}
