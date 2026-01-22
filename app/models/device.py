from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    supabase_user_id = Column(
        UUID(as_uuid=True), nullable=False, unique=True, index=True
    )
    token = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
