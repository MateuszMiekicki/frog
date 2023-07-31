from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from entity.base import Base
from entity.sensor import Sensor


class Device(Base):
    __tablename__ = 'device'
    sensors = relationship('Sensor', backref='sensor',
                           cascade="all, delete-orphan")

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    mac_address = Column(String, nullable=False, unique=True)
    name = Column(String)
