from datetime import time
from uuid import UUID

from pydantic import BaseModel


class AvailabilityCreate(BaseModel):
    weekday: str
    start_time: time
    end_time: time


class AvailabilityPublic(AvailabilityCreate):
    id: UUID

    class Config:
        from_attributes = True
