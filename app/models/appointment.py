import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class AppointmentStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    therapist_id = Column(
        UUID(as_uuid=True), ForeignKey("therapists.id"), nullable=False
    )
    treatment_id = Column(
        UUID(as_uuid=True), ForeignKey("treatments.id"), nullable=False
    )
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(
        Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.scheduled
    )
    notes = Column(Text)

    patient = relationship("Patient")
    therapist = relationship("Therapist")
    treatment = relationship("Treatment")
