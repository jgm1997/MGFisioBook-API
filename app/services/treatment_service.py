from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.treatment import Treatment
from app.schemas.treatment import TreatmentCreate, TreatmentUpdate


async def create_treatment(db: AsyncSession, data: TreatmentCreate) -> Treatment:
    treatment = Treatment(
        name=data.name,
        description=data.description,
        duration_minutes=data.duration_minutes,
        price=data.price,
    )

    db.add(treatment)
    await db.commit()
    await db.refresh(treatment)
    return treatment


async def get_treatment(db: AsyncSession, treatment_id: UUID) -> Optional[Treatment]:
    query = select(Treatment).where(Treatment.id == treatment_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_treatments(db: AsyncSession) -> list[Treatment]:
    query = select(Treatment)
    result = await db.execute(query)
    return result.scalars().all()


async def update_treatment(
    db: AsyncSession, treatment_id: UUID, data: TreatmentUpdate
) -> Treatment:
    treatment = await get_treatment(db, treatment_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(treatment, key, value)

    db.add(treatment)
    await db.commit()
    await db.refresh(treatment)
    return treatment
