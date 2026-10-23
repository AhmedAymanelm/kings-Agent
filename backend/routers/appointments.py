"""
routers/appointments.py — Appointments endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.appointment import Appointment
from ..schemas.appointment import AppointmentOut

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/", response_model=list[AppointmentOut])
def list_appointments(db: Session = Depends(get_db)):
    return db.query(Appointment).order_by(Appointment.id).all()


@router.post("/{appt_id}/confirm", response_model=AppointmentOut)
def confirm_appointment(appt_id: int, db: Session = Depends(get_db)):
    a = db.get(Appointment, appt_id)
    if not a:
        raise HTTPException(404, "Not found")
    a.confirmed = True
    db.commit()
    db.refresh(a)
    return a
