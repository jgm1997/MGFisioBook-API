from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.treatment import TreatmentCreate, TreatmentPublic
from app.services.treatment_service import (
    create_treatment,
    get_treatment,
    list_treatments,
    update_treatment,
)

router = APIRouter()


@router.post("/", response_model=TreatmentPublic)
async def create_treatment_endpoint(
    data: TreatmentCreate, db: AsyncSession = Depends(get_db)
):
    return await create_treatment(db, data)


@router.get("/{treatment_id}", response_model=TreatmentPublic)
async def get_treatment_endpoint(treatment_id: str, db: AsyncSession = Depends(get_db)):
    return await get_treatment(db, treatment_id)


@router.get("/", response_model=list[TreatmentPublic])
async def list_treatments_endpoint(db: AsyncSession = Depends(get_db)):
    return await list_treatments(db)


@router.put("/{treatment_id}", response_model=TreatmentPublic)
async def update_treatment_endpoint(
    treatment_id: str,
    data: TreatmentCreate,
    db: AsyncSession = Depends(get_db),
):
    return await update_treatment(db, treatment_id, data)
