from pydantic import BaseModel, Field


class Sensor(BaseModel):
    device_id: int = Field(min=1)
    name: str
    pin: int = Field(min=1)
    type: str
    min_value: float
    max_value: float
