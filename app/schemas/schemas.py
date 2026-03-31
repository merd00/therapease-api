from pydantic import BaseModel
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
    title: Optional[str] = None
    clinic_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None                    # ← YENİ
    specializations: Optional[str] = None        # ← YENİ
    work_hours: Optional[str] = None             # ← YENİ
    session_fee: Optional[int] = None            # ← YENİ
    created_at: Optional[datetime] = None        # ← YENİ

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# ── PROFİL ────────────────────────────────────────────────────────────────────
class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    clinic_name: Optional[str] = None
    bio: Optional[str] = None                    # ← YENİ
    specializations: Optional[str] = None        # ← YENİ
    work_hours: Optional[str] = None             # ← YENİ
    session_fee: Optional[int] = None            # ← YENİ

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# ── HASTA ─────────────────────────────────────────────────────────────────────
class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    phone: Optional[str] = None
    status: Optional[str] = "Aktif"
    tags: Optional[str] = None  

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[str] = None 

class PatientResponse(BaseModel):
    id: int
    name: str
    age: Optional[int]
    phone: Optional[str]
    status: str
    tags: Optional[str] = None 
    created_at: datetime

    class Config:
        from_attributes = True
        
# ── DANIŞAN ÖZET ──────────────────────────────────────────────────────────────
class PatientSummary(BaseModel):
    total_sessions: int
    completed_sessions: int
    cancelled_sessions: int
    last_appointment: Optional[str] = None
    next_appointment: Optional[str] = None
    last_appointment_date: Optional[str] = None
    next_appointment_date: Optional[str] = None
    
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
    patient_name: Optional[str] = None
    patient_age:   Optional[int] = None
    patient_phone: Optional[str] = None

    class Config:
        from_attributes = True

# ── NOT ───────────────────────────────────────────────────────────────────────
class NoteCreate(BaseModel):
    content: str
    patient_id: int
    title: Optional[str] = None 
    session_number: Optional[int] = None
    created_at: Optional[datetime] = None 

class NoteUpdate(BaseModel):             
    title: Optional[str] = None
    content: Optional[str] = None
    session_number: Optional[int] = None
    created_at: Optional[datetime] = None 
    
class NoteResponse(BaseModel):
    id: int
    content: str
    title: Optional[str] = None 
    session_number: Optional[int] = None  
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True