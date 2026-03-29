from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from app.routers.patients import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/")
def get_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    total_patients = db.query(models.Patient).filter(
        models.Patient.doctor_id == current_user.id
    ).count()

    active_patients = db.query(models.Patient).filter(
        models.Patient.doctor_id == current_user.id,
        models.Patient.status == "Aktif"
    ).count()

    total_appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == current_user.id
    ).count()

    total_notes = db.query(models.Note).filter(
        models.Note.patient_id.in_(
            db.query(models.Patient.id).filter(
                models.Patient.doctor_id == current_user.id
            )
        )
    ).count()

    today_appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == current_user.id,
        models.Appointment.status != "İptal"
    ).all()

    return {
        "total_patients": total_patients,
        "active_patients": active_patients,
        "total_appointments": total_appointments,
        "total_notes": total_notes,
        "today_appointments": [
            {
                "id": a.id,
                "time": a.time,
                "date": a.date,
                "type": a.type,
                "status": a.status,
                "patient_id": a.patient_id,
            }
            for a in today_appointments
        ]
    }