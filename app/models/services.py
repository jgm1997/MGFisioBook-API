from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ServiceBase(BaseModel):
    name: str
    duration: int  # in minutes
    price: float


class ServiceCreate(ServiceBase):
    pass


class Service(ServiceBase):
    id: UUID
    created_at: datetime
