from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class PatientBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class PatientCreate(PatientBase):
    pass


class Patient(PatientBase):
    id: UUID
    created_at: datetime
