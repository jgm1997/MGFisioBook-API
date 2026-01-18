from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.patient import Patient
from app.models.promote_user import PromoteUserRequest
from app.models.therapist import Therapist

router = APIRouter()


@router.put("/promote-user/{user_id}")
async def promote_user(
    user_id: UUID,
    data: PromoteUserRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    query = select(Patient).where(Patient.supabase_user_id == user_id)
    result = await db.execute(query)
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        await db.delete(patient)
        await db.commit()

    new_therapist = Therapist(
        name=f"{patient.first_name} {patient.last_name}",
        specialty="Admin",
        phone=patient.phone,
        email=patient.email,
    )
    db.add(new_therapist)
    await db.commit()
    await db.refresh(new_therapist)
    return {
        "detail": f"User {new_therapist.name} promoted to {data.role} successfully."
    }
