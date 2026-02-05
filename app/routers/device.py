import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.device import Device

router = APIRouter()


@router.post("")
async def register_device(
    token: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    # user may be a dict in tests or an object in real deps
    user_id = (
        user["id"]
        if isinstance(user, dict) and "id" in user
        else getattr(user, "id", None)
    )

    # normalize to uuid.UUID when possible (Device.supabase_user_id is UUID)
    supabase_user_id = None
    try:
        supabase_user_id = uuid.UUID(str(user_id)) if user_id is not None else None
    except Exception:
        supabase_user_id = None

    query = select(Device).where(Device.token == token)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        return {"status": "already registered"}

    device = Device(supabase_user_id=supabase_user_id, token=token, platform="unknown")
    db.add(device)
    await db.commit()
    return {"status": "registered"}
