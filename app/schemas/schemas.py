from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ── AUTH ──────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# ── HASTA ─────────────────────────────────────────────────────────────────────
class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    phone: Optional[str] = None
    status: Optional[str] = "Aktif"

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    status: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    name: str
    age: Optional[int]
    phone: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# ── RANDEVU ───────────────────────────────────────────────────────────────────
class AppointmentCreate(BaseModel):
    date: str
    time: str
    type: str
    duration: Optional[int] = 50
    status: Optional[str] = "Beklemede"
    patient_id: int

class AppointmentUpdate(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    type: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    date: str
    time: str
    type: str
    duration: int
    status: str
    patient_id: int

    class Config:
        from_attributes = True

# ── NOT ───────────────────────────────────────────────────────────────────────
class NoteCreate(BaseModel):
    content: str
    patient_id: int

class NoteResponse(BaseModel):
    id: int
    content: str
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True