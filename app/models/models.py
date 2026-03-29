from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False)
    email       = Column(String, unique=True, index=True, nullable=False)
    password    = Column(String, nullable=False)
    role        = Column(String, default="psikolog")
    title       = Column(String, nullable=True)        # ← YENİ: Uzman Psikolog
    clinic_name = Column(String, nullable=True)        # ← YENİ: Klinik adı
    avatar_url  = Column(String, nullable=True)        # ← YENİ: Fotoğraf URL
    created_at  = Column(DateTime, default=datetime.utcnow)

    patients     = relationship("Patient", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

# Patient, Appointment, Note modelleri aynı kalıyor...
class Patient(Base):
    __tablename__ = "patients"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    age        = Column(Integer)
    phone      = Column(String)
    status     = Column(String, default="Aktif")
    doctor_id  = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    doctor       = relationship("User", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient")
    notes        = relationship("Note", back_populates="patient")

class Appointment(Base):
    __tablename__ = "appointments"

    id         = Column(Integer, primary_key=True, index=True)
    date       = Column(String, nullable=False)
    time       = Column(String, nullable=False)
    type       = Column(String, nullable=False)
    duration   = Column(Integer, default=50)
    status     = Column(String, default="Beklemede")
    doctor_id  = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))

    doctor  = relationship("User", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")

class Note(Base):
    __tablename__ = "notes"

    id         = Column(Integer, primary_key=True, index=True)
    content    = Column(Text, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="notes")