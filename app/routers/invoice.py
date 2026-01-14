from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.appointment import Appointment
from app.schemas.invoice import InvoicePublic
from app.services.invoice_service import (
    get_invoice,
    list_invoices,
    list_patient_invoices,
    mark_invoice_paid,
)
from app.services.patient_service import get_patient

router = APIRouter()


@router.post("/", response_model=list[InvoicePublic])
async def list_invoices_endpoint(
    db: AsyncSession = Depends(get_db), user=Depends(require_role("admin"))
):
    return await list_invoices(db)


@router.get("/my", response_model=list[InvoicePublic])
async def list_my_invoices(
    db: AsyncSession = Depends(get_db), user=Depends(require_role("patient"))
):
    patient = await get_patient(db, user["id"])
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    query = select(Appointment.id).where(Appointment.patient_id == patient.id)
    result = await db.execute(query)
    appointment_ids = [row[0] for row in result.all()]

    return await list_patient_invoices(db, appointment_ids)


@router.get("/{invoice_id}", response_model=InvoicePublic)
async def get_invoice_endpoint(
    invoice_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    invoice = await get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if user["role"] != "admin":
        if user["role"] != "patient":
            raise HTTPException(
                status_code=403, detail="Not authorized to access this invoice"
            )

        query = select(Appointment).where(Appointment.id == invoice.appointment_id)
        result = await db.execute(query)
        appointment = result.scalar_one_or_none()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        patient = await get_patient(db, user["id"])
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this invoice"
            )

    return invoice


@router.put("/{invoice_id}/pay", response_model=InvoicePublic)
async def mark_invoice_paid_endpoint(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin")),
):
    invoice = await get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return await mark_invoice_paid(db, invoice)
