from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.patients import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("/", response_model=List[schemas.NoteResponse])
def get_notes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Bu doktorun hastalarına ait notları getir
    patient_ids = [
        p.id for p in db.query(models.Patient).filter(
            models.Patient.doctor_id == current_user.id
        ).all()
    ]
    return db.query(models.Note).filter(
        models.Note.patient_id.in_(patient_ids)
    ).all()

@router.post("/", response_model=schemas.NoteResponse)
def create_note(
    data: schemas.NoteCreate,
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

    note = models.Note(**data.model_dump())
    db.add(note)
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
        models.Note.id == note_id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Not bulunamadı")

    db.delete(note)
    db.commit()
    return {"message": "Not silindi"}