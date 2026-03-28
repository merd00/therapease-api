from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.patients import get_current_user

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.get("/", response_model=List[schemas.AppointmentResponse])
def get_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Appointment).filter(
        models.Appointment.doctor_id == current_user.id
    ).all()

@router.post("/", response_model=schemas.AppointmentResponse)
def create_appointment(
    data: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Hasta bu doktora ait mi?
    patient = db.query(models.Patient).filter(
        models.Patient.id == data.patient_id,
        models.Patient.doctor_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Hasta bulunamadı")

    appointment = models.Appointment(
        **data.model_dump(),
        doctor_id=current_user.id
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment

@router.put("/{appointment_id}", response_model=schemas.AppointmentResponse)
def update_appointment(
    appointment_id: int,
    data: schemas.AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.doctor_id == current_user.id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(appointment, key, value)

    db.commit()
    db.refresh(appointment)
    return appointment

@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id,
        models.Appointment.doctor_id == current_user.id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Randevu bulunamadı")

    db.delete(appointment)
    db.commit()
    return {"message": "Randevu silindi"}