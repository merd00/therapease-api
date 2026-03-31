# reset_db.py — therapease-api/ klasörüne koy
from app.database import Base, engine
from app.models import models  # tüm modeller import edilsin

print("Tablolar siliniyor...")
Base.metadata.drop_all(bind=engine)

print("Tablolar yeniden oluşturuluyor...")
Base.metadata.create_all(bind=engine)

print("✅ Veritabanı sıfırlandı.")