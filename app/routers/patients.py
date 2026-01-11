from fastapi import APIRouter, Depends, HTTPException
from httpx import delete

from app.auth import authorize, get_current_user
from app.db import get_supabase
from app.models.patients import Patient, PatientCreate


router = APIRouter()
supabase = get_supabase()


@router.post("", response_model=Patient)
def create_patient(patient: PatientCreate, user=Depends(authorize(["admin"]))):
    existing = (
        supabase.table("patients")
        .select("*")
        .eq("email", patient.email)
        .single()
        .execute()
    )
    if existing.data:
        raise HTTPException(
            status_code=400, detail="Patient with this email already exists"
        )
    response = supabase.table("patients").insert(patient.model_dump()).execute()
    return response.data[0]


@router.get("", response_model=list[Patient])
def list_patients(user=Depends(authorize(["admin", "staff"]))):
    response = supabase.table("patients").select("*").execute()
    return response.data


@router.get("/me", response_model=Patient)
def get_my_profile(user=Depends(authorize(["patient"]))):
    response = (
        supabase.table("patients").select("*").eq("id", user["id"]).single().execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return response.data


@router.get("/{patient_id}", response_model=Patient)
def get_patient(patient_id: str):
    response = (
        supabase.table("patients").select("*").eq("id", patient_id).single().execute()
    )
    return response.data


@router.patch("/{patient_id}", response_model=Patient)
def update_patient(
    patient_id: str, updates: PatientCreate, user=Depends(authorize(["admin"]))
):
    response = (
        supabase.table("patients")
        .update(updates.model_dump(exclude_unset=True))
        .eq("id", patient_id)
        .execute()
    )
    return response.data[0]


@router.delete("/{patient_id}")
def delete_patient(patient_id: str, user=Depends(authorize(["admin"]))):
    response = supabase.table("patients").delete().eq("id", patient_id).execute()
    return response.data[0]
