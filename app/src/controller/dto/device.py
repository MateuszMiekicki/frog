from pydantic import BaseModel, EmailStr, SecretStr, Field
from pydantic.typing import Optional


class Device(BaseModel):
    name: str
    key: str = Field(min_length=27, max_length=128)


class Sensor(BaseModel):
    device_id: int = Field(min=1)
    name: str

