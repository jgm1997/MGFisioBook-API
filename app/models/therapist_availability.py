import uuid

from sqlalchemy import Column, ForeignKey, String, Time
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class TherapistAvailability(Base):
    __tablename__ = "therapist_availability"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    therapist_id = Column(
        UUID(as_uuid=True), ForeignKey("therapists.id"), nullable=False
    )
    weekday = Column(String, nullable=False)  # e.g., 'Monday', 'Tuesday', etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
