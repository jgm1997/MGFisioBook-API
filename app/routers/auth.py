from fastapi import APIRouter, Depends, HTTPException

from app.auth import authorize, get_current_user
from app.db import get_supabase


router = APIRouter()
supabase = get_supabase()


@router.post("/register")
def register(user=Depends(get_current_user)):
    auth_user_id = user["sub"]
    email = user["email"]

    response = (
        supabase.table("users")
        .insert(
            {
                "auth_user_id": auth_user_id,
                "username": email.split("@")[0],
                "role": "patient",
            }
        )
        .execute()
    )

    return {"message": "User registered with role 'patient'", "user": response.data[0]}

@router.get("/users")
def list_users(user=Depends(authorize(["admin"]))):
    response = supabase.table("users").select("*").execute()
    return response.data

@router.patch("/users/{user_id}/role")
def update_role(user_id: str, new_role: str, user=Depends(authorize(["admin"]))):
    response = (
        supabase.table("users").update({"role": new_role}).eq("id", user_id).execute()
    )
    return response.data[0]
