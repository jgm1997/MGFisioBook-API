from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

import app
from app.auth import authorize, get_current_user
from app.db import get_supabase
from app.models.appointments import Appointment, AppointmentCreate


router = APIRouter()
supabase = get_supabase()


@router.post("", response_model=Appointment)
def create_appointment(
    appointment: AppointmentCreate,
    user=Depends(authorize(["admin", "staff", "patient"])),
):
    if appointment.scheduled_at < datetime.now():
        raise HTTPException(
            status_code=400, detail="Appointment time must be in the future"
        )

    patient = (
        supabase.table("patients")
        .select("*")
        .eq("id", str(appointment.patient_id))
        .single()
        .execute()
    )
    if not patient.data:
        raise HTTPException(status_code=404, detail="Patient not found")

    service = (
        supabase.table("services")
        .select("*")
        .eq("id", str(appointment.service_id))
        .single()
        .execute()
    )
    if not service.data:
        raise HTTPException(status_code=404, detail="Service not found")

    if user["role"] == "patient" and str(appointment.patient_id) != str(user["id"]):
        raise HTTPException(
            status_code=403, detail="Patients can only create their own appointments"
        )

    response = supabase.table("appointments").insert(appointment.model_dump()).execute()
    return response.data[0]


@router.get("", response_model=list[Appointment])
def list_appointments(user=Depends(authorize(["admin", "staff", "patient"]))):
    role = user["role"]
    if role in ["admin", "staff"]:
        response = supabase.table("appointments").select("*").execute()
    else:
        response = (
            supabase.table("appointments")
            .select("*")
            .eq("patient_id", user["id"])
            .execute()
        )

    return response.data


@router.get("/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: str):
    response = (
        supabase.table("appointments")
        .select("*")
        .eq("id", appointment_id)
        .single()
        .execute()
    )
    return response.data


@router.patch("/{appointment_id}", response_model=Appointment)
def update_appointment(
    appointment_id: str,
    updates: AppointmentCreate,
    user=Depends(authorize(["admin", "staff"])),
):
    if updates.scheduled_at < datetime.now():
        raise HTTPException(
            status_code=400, detail="Appointment time must be in the future"
        )

    response = (
        supabase.table("appointments")
        .update(updates.model_dump(exclude_unset=True))
        .eq("id", appointment_id)
        .execute()
    )
    return response.data[0]


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: str, user=Depends(authorize(["admin", "staff"]))
):
    response = (
        supabase.table("appointments").delete().eq("id", appointment_id).execute()
    )
    return response.data[0]
