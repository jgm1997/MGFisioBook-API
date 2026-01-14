from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.treatment import Treatment
from app.services.free_slot_service import get_free_slots

router = APIRouter()


@router.get("/")
async def free_slots_endpoint(
    therapist_id: UUID, treatment_id: UUID, day: str, db: AsyncSession = Depends(get_db)
):
    try:
        day_obj = date.fromisoformat(day)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Expected YYYY-MM-DD."
        )

    query = select(Treatment).where(Treatment.id == treatment_id)
    result = await db.execute(query)
    treatment = result.scalar_one_or_none()
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")

    return await get_free_slots(db, therapist_id, day_obj, treatment.duration_minutes)
