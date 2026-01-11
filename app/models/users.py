from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    role: str  # "admin" or "staff"


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: UUID
    created_at: datetime
