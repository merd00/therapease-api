from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.patients import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    current_user: models.User = Depends(get_current_user)
):
    return current_user


@router.put("/me", response_model=schemas.UserResponse)
def update_me(
    data: schemas.UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user


# ── YENİ: İstatistikler ──────────────────────────────────────────────────────
@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    today     = date.today()
    this_month_start = today.replace(day=1).isoformat()

    # Danışanlar
    total_patients = db.query(models.Patient).filter(
        models.Patient.doctor_id == current_user.id
    ).count()

    # Tüm randevular
    all_appts = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == current_user.id
    ).all()

    total_appts     = len(all_appts)
    completed_appts = len([a for a in all_appts if a.status == "Onaylı"])
    cancelled_appts = len([a for a in all_appts if a.status == "İptal"])
    completion_rate = round(completed_appts / total_appts * 100) if total_appts > 0 else 0

    # Bu ay randevular
    this_month_appts     = [a for a in all_appts if a.date >= this_month_start]
    this_month_completed = len([a for a in this_month_appts if a.status == "Onaylı"])
    this_month_total     = len(this_month_appts)

    # Gelir hesabı
    fee = current_user.session_fee or 0
    total_income      = completed_appts * fee
    this_month_income = this_month_completed * fee

    # En çok yapılan randevu türü
    type_counts = {}
    for a in all_appts:
        type_counts[a.type] = type_counts.get(a.type, 0) + 1
    most_common_type = max(type_counts, key=type_counts.get) if type_counts else None

    # Toplam not
    total_notes = db.query(models.Note).filter(
        models.Note.doctor_id == current_user.id
    ).count()

    return {
        # Danışan
        "total_patients":        total_patients,
        # Randevu
        "total_appointments":    total_appts,
        "completed_appointments": completed_appts,
        "cancelled_appointments": cancelled_appts,
        "completion_rate":       completion_rate,
        "most_common_type":      most_common_type,
        # Bu ay
        "this_month_total":      this_month_total,
        "this_month_completed":  this_month_completed,
        # Not
        "total_notes":           total_notes,
        # Gelir
        "session_fee":           fee,
        "total_income":          total_income,
        "this_month_income":     this_month_income,
    }