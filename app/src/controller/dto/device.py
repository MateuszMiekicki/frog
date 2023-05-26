from pydantic import BaseModel, Field


class Device(BaseModel):
    name: str
    key: str = Field(min_length=27, max_length=128)
