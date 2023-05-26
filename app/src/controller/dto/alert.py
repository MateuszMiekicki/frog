from pydantic import BaseModel, Field


class Alert(BaseModel):
    sensor_id: int = Field(min=1)
    name: str
    min_value: float
    max_value: float
