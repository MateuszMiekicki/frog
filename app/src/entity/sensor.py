from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from entity.base import Base
from sqlalchemy.orm import backref


class Sensor(Base):
    __tablename__ = 'sensor'

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey(
        'device.id', ondelete='CASCADE'), nullable=False)
    pin_number = Column(Integer, nullable=False, unique=True)
    name = Column(String)
    type = Column(String)
    min_value = Column(Integer)
    max_value = Column(Integer)

    device = relationship('Device', back_populates='sensors')
    alerts = relationship('Alert', back_populates='sensor',
                          cascade='all, delete-orphan')
