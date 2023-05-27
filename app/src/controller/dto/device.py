from pydantic import BaseModel, Field


class Device(BaseModel):
    name: str
    key: str = Field(max_length=17)
