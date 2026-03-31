from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.patients import get_current_user

router = APIRouter(prefix="/appointments", tags=["appointments"])


def time_to_minutes(t: str) -> int:
    h, m = map(int, t.split(':'))
    return h * 60 + m


def check_conflict(db, doctor_id: int, date: str, time: str, duration: int, exclude_id: int = None):
    new_start = time_to_minutes(time)
    new_end   = new_start + duration

    existing = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id,
        models.Appointment.date == date,
        models.Appointment.status != "İptal",
    )
    if exclude_id:
        existing = existing.filter(models.Appointment.id != exclude_id)

    for appt in existing.all():
        ex_start = time_to_minutes(appt.time)
        ex_end   = ex_start + appt.duration

        if new_start < ex_end and new_end > ex_start:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"{appt.time} - {ex_end // 60:02d}:{ex_end % 60:02d} saatleri arasında "
                    f"zaten bir randevu var ({appt.duration} dk)"
                )
            )


def patient_info(patient):
    return {
        "patient_name":  patient.name  if patient else "Bilinmeyen",
        "patient_age":   patient.age   if patient else None,
        "patient_phone": patient.phone if patient else None,
    }


@router.get("/", response_model=List[schemas.AppointmentResponse])
def get_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == current_user.id
    ).order_by(models.Appointment.date.desc(), models.Appointment.time.desc()).all()

    result = []
    for appt in appointments:
        patient = db.query(models.Patient).filter(
            models.Patient.id == appt.patient_id
        ).first()
        result.append({
            "id":       appt.id,
            "date":     appt.date,
            "time":     appt.time,
            "type":     appt.type,
            "duration": appt.duration,
            "status":   appt.status,
            "patient_id": appt.patient_id,
            **patient_info(patient),
        })
    return result


@router.post("/", response_model=schemas.AppointmentResponse)
def create_appointment(
    data: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == data.patient_id,
        models.Patient.doctor_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Danışan bulunamadı")

    check_conflict(db, current_user.id, data.date, data.time, data.duration)

    appointment = models.Appointment(
        **data.model_dump(),
        doctor_id=current_user.id
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return {
        "id":       appointment.id,
        "date":     appointment.date,
        "time":     appointment.time,
        "type":     appointment.type,
        "duration": appointment.duration,
        "status":   appointment.status,
        "patient_id": appointment.patient_id,
        **patient_info(patient),
    }


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

    new_date     = data.date     or appointment.date
    new_time     = data.time     or appointment.time
    new_duration = data.duration or appointment.duration
    new_status   = data.status   or appointment.status

    if new_status != "İptal":
        check_conflict(
            db, current_user.id,
            new_date, new_time, new_duration,
            exclude_id=appointment_id
        )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(appointment, key, value)

    db.commit()
    db.refresh(appointment)

    patient = db.query(models.Patient).filter(
        models.Patient.id == appointment.patient_id
    ).first()

    return {
        "id":       appointment.id,
        "date":     appointment.date,
        "time":     appointment.time,
        "type":     appointment.type,
        "duration": appointment.duration,
        "status":   appointment.status,
        "patient_id": appointment.patient_id,
        **patient_info(patient),
    }


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