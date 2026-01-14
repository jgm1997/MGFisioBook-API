from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import appointment, auth, availability, patient, therapist

app = FastAPI(title="MGFisioBook API")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(patient.router, prefix="/patients", tags=["patients"])
app.include_router(therapist.router, prefix="/therapists", tags=["therapists"])
app.include_router(appointment.router, prefix="/appointments", tags=["appointments"])
app.include_router(availability.router, prefix="/availability", tags=["availability"])
