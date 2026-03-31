from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.patients import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=List[schemas.NoteResponse])
def get_notes(
    patient_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Note).filter(
        models.Note.doctor_id == current_user.id
    )
    if patient_id is not None:
        query = query.filter(models.Note.patient_id == patient_id)
    return query.order_by(models.Note.created_at.desc()).all()


@router.get("/by-patient")
def get_notes_by_patient(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patients = db.query(models.Patient).filter(
        models.Patient.doctor_id == current_user.id
    ).all()

    result = []
    for patient in patients:
        count = db.query(models.Note).filter(
            models.Note.patient_id == patient.id,
            models.Note.doctor_id == current_user.id
        ).count()
        result.append({
            "patient_id":   patient.id,
            "patient_name": patient.name,
            "count":        count,
        })

    result.sort(key=lambda x: x["count"], reverse=True)
    return result


@router.post("/", response_model=schemas.NoteResponse)
def create_note(
    data: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    patient = db.query(models.Patient).filter(
        models.Patient.id == data.patient_id,
        models.Patient.doctor_id == current_user.id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Danışan bulunamadı")

    # Seans numarası: manuel geldiyse onu kullan, gelmediyse otomatik hesapla
    if data.session_number is not None:
        session_number = data.session_number
    else:
        existing_count = db.query(models.Note).filter(
            models.Note.patient_id == data.patient_id,
            models.Note.doctor_id == current_user.id
        ).count()
        session_number = existing_count + 1

    # Tarih: manuel geldiyse onu kullan, gelmediyse şimdiki zaman
    created_at = data.created_at if data.created_at else datetime.utcnow()

    note = models.Note(
        title=data.title,
        content=data.content,
        patient_id=data.patient_id,
        doctor_id=current_user.id,
        session_number=session_number,
        created_at=created_at,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.put("/{note_id}", response_model=schemas.NoteResponse)
def update_note(
    note_id: int,
    data: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.doctor_id == current_user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Not bulunamadı")

    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content
    if data.session_number is not None:
        note.session_number = data.session_number
    if data.created_at is not None:
        note.created_at = data.created_at

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.doctor_id == current_user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Not bulunamadı")

    db.delete(note)
    db.commit()
    return {"message": "Not silindi"}