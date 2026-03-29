from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserResponse, UpdateProfileRequest, ChangePasswordRequest
from app.routers.auth import get_current_user
import shutil, os, uuid

router = APIRouter(prefix="/users", tags=["users"])

# ── Mevcut kullanıcıyı getir ──────────────────────────────────────────────────
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# ── Profil bilgilerini güncelle ───────────────────────────────────────────────
@router.put("/me", response_model=UserResponse)
def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.name is not None:
        current_user.name = data.name
    if data.title is not None:
        current_user.title = data.title
    if data.clinic_name is not None:
        current_user.clinic_name = data.clinic_name

    db.commit()
    db.refresh(current_user)
    return current_user

# ── Şifre değiştir ───────────────────────────────────────────────────────────
@router.put("/me/password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    if not pwd_context.verify(data.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Mevcut şifre hatalı")

    current_user.password = pwd_context.hash(data.new_password)
    db.commit()
    return {"message": "Şifre başarıyla güncellendi"}

# ── Avatar yükle ──────────────────────────────────────────────────────────────
@router.post("/me/avatar", response_model=UserResponse)
def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Sadece resim dosyası kabul et
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Sadece JPG, PNG veya WEBP yükleyebilirsiniz")

    # Klasör yoksa oluştur
    os.makedirs("avatars", exist_ok=True)

    # Benzersiz dosya adı oluştur
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = f"avatars/{filename}"

    # Dosyayı kaydet
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # URL'yi veritabanına kaydet
    current_user.avatar_url = f"/avatars/{filename}"
    db.commit()
    db.refresh(current_user)
    return current_user