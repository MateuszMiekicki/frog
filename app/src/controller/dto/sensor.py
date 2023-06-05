from pydantic import BaseModel, Field


class Sensor(BaseModel):
    name: str
    pin_number: int = Field(min=1)
    type: str
    min_value: float
    max_value: float
