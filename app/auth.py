from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt

from app.db import SUPABASE_SECRET_KEY, get_supabase


security = HTTPBearer()


def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(
            token.credentials, SUPABASE_SECRET_KEY, algorithms=["HS256"]
        )
        auth_user_id = payload.get("sub")
        supabase = get_supabase()
        user = (
            supabase.table("users")
            .select("*")
            .eq("id", auth_user_id)
            .single()
            .execute()
        )
        if not user.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not registered in app",
            )
        return user.data
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


def authorize(required_roles: list[str]):
    def wrapper(user=Depends(get_current_user)):
        if user["role"] not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this action",
            )
        return user

    return wrapper
