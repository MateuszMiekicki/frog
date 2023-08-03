from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from entity.base import Base
from entity.sensor import Sensor
from sqlalchemy.orm import backref


class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)
    mac_address = Column(String, nullable=False, unique=True)
    name = Column(String)

    user = relationship('User', back_populates='devices')
    sensors = relationship('Sensor', back_populates='device', cascade='all, delete-orphan')
    alerts = relationship('Alert', back_populates='device', cascade='all, delete-orphan')  # Add this line
