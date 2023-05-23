from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from entity.base import Base


class Sensor(Base):
    __tablename__ = 'sensor'

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('device.id'), nullable=False)
    pin = Column(Integer, nullable=False, unique=True)
    name = Column(String)