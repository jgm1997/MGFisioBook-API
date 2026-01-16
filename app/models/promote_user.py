from proto import Field
from pydantic import BaseModel


class PromoteUserRequest(BaseModel):
    role: str = Field(..., regex="^(therapist|admin)$x")
