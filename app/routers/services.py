from fastapi import APIRouter, Depends, HTTPException

from app.auth import authorize
from app.db import get_supabase
from app.models.services import Service, ServiceCreate


router = APIRouter()
supabase = get_supabase()


@router.post("", response_model=Service)
def create_service(service: ServiceCreate, user=Depends(authorize(["admin"]))):
    if service.duration < 0:
        raise HTTPException(
            status_code=400, detail="Service duration must be non-negative"
        )
    if service.price < 0.0:
        raise HTTPException(
            status_code=400, detail="Service price must be non-negative"
        )

    response = supabase.table("services").insert(service.model_dump()).execute()
    return response.data[0]


@router.get("", response_model=list[Service])
def list_services(user=Depends(authorize(["admin", "staff", "patient"]))):
    response = supabase.table("services").select("*").execute()
    return response.data


@router.get("/{service_id}", response_model=Service)
def get_service(service_id: str):
    response = (
        supabase.table("services").select("*").eq("id", service_id).single().execute()
    )
    return response.data


@router.patch("/{service_id}", response_model=Service)
def update_service(
    service_id: str, updates: ServiceCreate, user=Depends(authorize(["admin"]))
):
    if updates.duration < 0:
        raise HTTPException(
            status_code=400, detail="Service duration must be non-negative"
        )
    if updates.price < 0.0:
        raise HTTPException(
            status_code=400, detail="Service price must be non-negative"
        )

    response = (
        supabase.table("services")
        .update(updates.model_dump(exclude_unset=True))
        .eq("id", service_id)
        .execute()
    )
    return response.data[0]


@router.delete("/{service_id}")
def delete_service(service_id: str, user=Depends(authorize(["admin"]))):
    response = supabase.table("services").delete().eq("id", service_id).execute()
    return response.data[0]
