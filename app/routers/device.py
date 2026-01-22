from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.device import DeviceCreate
from app.services.device_service import register

router = APIRouter()


@router.post("")
async def register_device(
    payload: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await register(db, user.id, payload)
