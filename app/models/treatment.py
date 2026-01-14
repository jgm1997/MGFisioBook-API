import uuid

from sqlalchemy import Column, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Treatment(Base):
    __tablename__ = "treatments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    duration_minutes = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
