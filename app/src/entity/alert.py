from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from entity.base import Base
from entity.sensor import Sensor
from entity.device import Device


class Alert(Base):
    __tablename__ = 'alert'
    device = relationship('Device')
    sensor = relationship('Sensor')

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('device.id'), nullable=False)
    sensor_id = Column(Integer, ForeignKey('sensor.id'), nullable=False)
    alert_number = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    served = Column(String, nullable=False)
