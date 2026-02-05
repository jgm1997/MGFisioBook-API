import uuid

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import synonym, validates

from app.models.base import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    supabase_user_id = Column(
        UUID(as_uuid=True), nullable=False, unique=True, index=True
    )
    # allow tests to construct with user_id kwarg
    user_id = synonym("supabase_user_id")

    token = Column(String, nullable=False)
    # provide default so tests can omit platform and DB constraint is satisfied
    platform = Column(
        String, nullable=False, default="unknown", server_default="unknown"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @validates("supabase_user_id")
    def _validate_supabase_user_id(self, key, value):
        if isinstance(value, str):
            try:
                return uuid.UUID(value)
            except Exception:
                return value
        return value
