from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from entity.base import Base


class Alert(Base):
    __tablename__ = 'alert'

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey(
        'device.id', ondelete='CASCADE'), nullable=False)
    sensor_id = Column(Integer, ForeignKey(
        'sensor.id', ondelete='CASCADE'), nullable=False)
    alert_number = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    served = Column(String, nullable=False)

    device = relationship('Device', back_populates='alerts')
    sensor = relationship('Sensor', back_populates='alerts')
