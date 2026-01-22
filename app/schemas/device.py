from pydantic import BaseModel


class DeviceCreate(BaseModel):
    token: str
    platform: str
