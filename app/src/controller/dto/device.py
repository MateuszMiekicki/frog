from pydantic import BaseModel, Field


class Device(BaseModel):
    name: str
    mac_address: str
