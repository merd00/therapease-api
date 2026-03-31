from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database import get_db
from app.models import models
from app.schemas import schemas
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/patients", tags=["patients"])

SECRET_KEY = "gizli-anahtar-bunu-degistir"
ALGORITHM  = "HS256"
security   = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user    = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Geçersiz token")


@router.get("/", response_model=List[schemas.PatientResponse])
def get_patients(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Patient).filter(
        models.Patient.doctor_id == current_user.id
    ).all()


@router.post("/", response_model=schemas.PatientResponse)
def create_patient(
    patient_data: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = models.Patient(
        **patient_data.model_dump(),
        doctor_id=current_user.id
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=schemas.PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id,
        models.Patient.doctor_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Danışan bulunamadı")
    return patient


# ── YENİ: Danışan özet istatistikleri ────────────────────────────────────────
@router.get("/{patient_id}/summary")
def get_patient_summary(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id,
        models.Patient.doctor_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Danışan bulunamadı")

    appointments = db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient_id,
        models.Appointment.doctor_id == current_user.id
    ).all()

    today = date.today().isoformat()

    total     = len(appointments)
    completed = len([a for a in appointments if a.status == "Onaylı"])
    cancelled = len([a for a in appointments if a.status == "İptal"])

    # Geçmiş randevular — en son olan
    past = sorted(
        [a for a in appointments if a.date < today],
        key=lambda a: (a.date, a.time), reverse=True
    )
    # Gelecek randevular — en yakın olan
    upcoming = sorted(
        [a for a in appointments if a.date >= today and a.status != "İptal"],
        key=lambda a: (a.date, a.time)
    )

    last_appt = past[0]     if past     else None
    next_appt = upcoming[0] if upcoming else None

    return {
        "total_sessions":      total,
        "completed_sessions":  completed,
        "cancelled_sessions":  cancelled,
        "last_appointment":      f"{last_appt.date} {last_appt.time}" if last_appt else None,
        "last_appointment_date": last_appt.date if last_appt else None,
        "next_appointment":      f"{next_appt.date} {next_appt.time}" if next_appt else None,
        "next_appointment_date": next_appt.date if next_appt else None,
    }


@router.put("/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(
    patient_id: int,
    patient_data: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id,
        models.Patient.doctor_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Danışan bulunamadı")

    for key, value in patient_data.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == patient_id,
        models.Patient.doctor_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Danışan bulunamadı")

    db.delete(patient)
    db.commit()
    return {"message": "Danışan silindi"}