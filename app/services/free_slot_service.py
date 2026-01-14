from datetime import date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus
from app.models.therapist_availability import TherapistAvailability


async def get_free_slots(
    db: AsyncSession, therapist_id: UUID, day: date, duration_minutes: int
) -> list[dict]:
    weekday = day.strftime("%A").lower()

    av_blocks_query = select(TherapistAvailability).where(
        TherapistAvailability.therapist_id == therapist_id,
        TherapistAvailability.weekday == weekday,
    )
    av_blocks_result = await db.execute(av_blocks_query)
    availability_blocks = av_blocks_result.scalars().all()
    if not availability_blocks:
        return []

    start_of_day = datetime.combine(day, time.min)
    end_of_day = datetime.combine(day, time.max)

    appt_query = select(Appointment).where(
        Appointment.therapist_id == therapist_id,
        Appointment.status == AppointmentStatus.scheduled,
        Appointment.start_time >= start_of_day,
        Appointment.end_time <= end_of_day,
    )
    appt_result = await db.execute(appt_query)
    appointments = appt_result.scalars().all()

    free_slots: list[dict] = []
    for block in availability_blocks:
        current = datetime.combine(day, block.start_time)
        block_end = datetime.combine(day, block.end_time)

        while current + timedelta(minutes=duration_minutes) <= block_end:
            slot_start = current
            slot_end = current + timedelta(minutes=duration_minutes)

            conflict = any(
                appt.start_time < slot_end and appt.end_time > slot_start
                for appt in appointments
            )
            if not conflict:
                free_slots.append(
                    {
                        "start_time": slot_start.isoformat(),
                        "end_time": slot_end.isoformat(),
                    }
                )
            current += timedelta(minutes=duration_minutes)
    return free_slots
