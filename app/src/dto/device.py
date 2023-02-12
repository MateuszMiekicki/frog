from pydantic import BaseModel, EmailStr, SecretStr, Field
from pydantic.typing import Optional


class Device(BaseModel):
    name: Optional[str] = None
    key: str = Field(min_length=27, max_length=128)


class Sensor(BaseModel):
    name: Optional[str] = None
