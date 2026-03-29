from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import models
from app.routers import auth
from app.routers import patients
from app.routers import appointments
from app.routers import notes
from app.routers import stats
from app.routers import users          
from fastapi.staticfiles import StaticFiles   
import os  

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TherapEase API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("avatars", exist_ok=True)
app.mount("/avatars", StaticFiles(directory="avatars"), name="avatars")

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(notes.router)
app.include_router(stats.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "TherapEase API çalışıyor"}