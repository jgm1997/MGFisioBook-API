from uuid import UUID

from firebase_admin import messaging
from sqlalchemy import cast, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import String

from app.models import appointment
from app.models.device import Device


async def send_push_to_user(db: AsyncSession, user_id: str, title: str, body: str):
    # Prefer matching by UUID when possible, otherwise compare string form
    result = None
    try:
        user_uuid = UUID(str(user_id))
        query = select(Device).where(Device.supabase_user_id == user_uuid)
        result = await db.execute(query)
    except Exception:
        query = select(Device).where(
            cast(Device.supabase_user_id, String) == str(user_id)
        )
        result = await db.execute(query)
    tokens = [row.token for row in result.scalars().all()]
    if not tokens:
        return

    # Try to find a related appointment (if user_id is a UUID)
    appointment_obj = None
    try:
        user_uuid = UUID(str(user_id))
        appointment_query = select(appointment.Appointment).where(
            appointment.Appointment.patient_id == user_uuid
        )
        appointment_result = await db.execute(appointment_query)
        appointment_obj = appointment_result.scalar_one_or_none()
    except Exception:
        appointment_obj = None

    data = {}
    if appointment_obj:
        data["appointmentId"] = str(appointment_obj.id)

    message_kwargs = {
        "notification": messaging.Notification(title=title, body=body),
        "tokens": tokens,
    }
    if data:
        message_kwargs["data"] = data

    message = messaging.MulticastMessage(**message_kwargs)

    messaging.send_each_for_multicast(message)
