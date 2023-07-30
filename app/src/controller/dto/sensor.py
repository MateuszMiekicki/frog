from pydantic import BaseModel, Field
from typing import Optional


class Sensor(BaseModel):
    id: Optional[int] = None
    name: str
    pin_number: int = Field(min=1)
    type: str
    min_value: float
    max_value: float
