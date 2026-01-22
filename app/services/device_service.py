from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.schemas.device import DeviceCreate


@staticmethod
async def register(db: AsyncSession, user_id: str, data: DeviceCreate):
    query = select(Device).where(Device.token == data.token)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    device = Device(
        user_id=user_id,
        token=data.token,
        platform=data.platform,
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device
