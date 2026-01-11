from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class AppointmentBase(BaseModel):
    patient_id: UUID
    service_id: UUID
    scheduled_at: datetime
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class Appointment(AppointmentBase):
    id: UUID
    created_at: datetime
