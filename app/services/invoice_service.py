from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment
from app.models.invoice import Invoice
from app.services.treatment_service import get_treatment


async def create_invoice_for_appointment(
    db: AsyncSession, appointment: Appointment
) -> Invoice:
    treatment = await get_treatment(db, appointment.treatment_id)
    invoice = Invoice(appointment_id=appointment.id, amount=treatment.price)
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def get_invoice(db: AsyncSession, invoice_id: UUID) -> Optional[Invoice]:
    query = select(Invoice).where(Invoice.id == invoice_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_invoices(db: AsyncSession) -> list[Invoice]:
    query = select(Invoice).order_by(Invoice.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def list_patient_invoices(
    db: AsyncSession, patient_appointment_ids: list[UUID]
) -> list[Invoice]:
    if not patient_appointment_ids:
        return []
    query = select(Invoice).where(Invoice.appointment_id.in_(patient_appointment_ids))
    result = await db.execute(query)
    return result.scalars().all()


async def mark_invoice_paid(db: AsyncSession, invoice: Invoice) -> Invoice:
    invoice.paid = True
    await db.commit()
    await db.refresh(invoice)
    return invoice
