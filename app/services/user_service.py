from app.core.supabase_client import supabase


def update_role(new_role: str):
    supabase.auth.update_user({"data": {"role": new_role}})
