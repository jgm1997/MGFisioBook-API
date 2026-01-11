from fastapi import FastAPI
from app.db import supabase
from app.routers import auth, patients, services, appointments

app = FastAPI(title="MGFisioBook API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(services.router, prefix="/services", tags=["services"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])


@app.get("/")
def root():
    return {"message": "MGFisioBook API is running"}


@app.get("/patients")
def list_patients():
    response = supabase.table("patients").select("*").execute()
    return response.data
