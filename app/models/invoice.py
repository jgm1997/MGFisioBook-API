import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(
        UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False
    )
    amount = Column(Numeric(10, 2), nullable=False)
    paid = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
