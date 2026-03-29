from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from app.routers.auth import get_current_user
from datetime import date, timedelta

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/")
def get_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    week_offset: int = Query(default=0)   # ← YENİ
):
    today = date.today()
    today_str = today.isoformat()

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

    # Bugünkü randevular
    today_appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == current_user.id,
        models.Appointment.date == today_str,
        models.Appointment.status != "İptal"
    ).all()

    # Tüm yaklaşan randevular (tarih+saat sıralı)
    all_appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == current_user.id,
        models.Appointment.status != "İptal"
    ).all()

    sorted_appointments = sorted(all_appointments, key=lambda a: (a.date, a.time))

    # Danışan id → isim map
    all_patient_ids = list(set([a.patient_id for a in all_appointments]))
    patients = db.query(models.Patient).filter(models.Patient.id.in_(all_patient_ids)).all()
    patient_map = {p.id: p.name for p in patients}

    # Son eklenen 4 danışan
    recent_patients = db.query(models.Patient).filter(
        models.Patient.doctor_id == current_user.id
    ).order_by(models.Patient.id.desc()).limit(4).all()

   # Haftalık seans — week_offset'e göre Pzt→Paz
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    day_names = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
    weekly = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        onaylı = db.query(models.Appointment).filter(
            models.Appointment.doctor_id == current_user.id,
            models.Appointment.date == day.isoformat(),
            models.Appointment.status == "Onaylı"
        ).count()
        beklemede = db.query(models.Appointment).filter(
            models.Appointment.doctor_id == current_user.id,
            models.Appointment.date == day.isoformat(),
            models.Appointment.status == "Beklemede"
        ).count()
        iptal = db.query(models.Appointment).filter(
            models.Appointment.doctor_id == current_user.id,
            models.Appointment.date == day.isoformat(),
            models.Appointment.status == "İptal"
        ).count()
        weekly.append({
            "day": day_names[i],
            "count": onaylı + beklemede + iptal,
            "onaylı": onaylı,
            "beklemede": beklemede,
            "iptal": iptal,
    })

    return {
        "total_patients": total_patients,
        "active_patients": active_patients,
        "total_appointments": total_appointments,
        "total_notes": total_notes,
        "today_count": len(today_appointments),
        "today_appointments": [
            {
                "id": a.id,
                "time": a.time,
                "date": a.date,
                "type": a.type,
                "status": a.status,
                "duration": a.duration,
                "patient_id": a.patient_id,
                "patient_name": patient_map.get(a.patient_id, "Bilinmeyen"),
            }
            for a in sorted_appointments
        ],
        "recent_patients": [
            {
                "id": p.id,
                "name": p.name,
                "status": p.status,
            }
            for p in recent_patients
        ],
        "weekly_sessions": weekly,
    }