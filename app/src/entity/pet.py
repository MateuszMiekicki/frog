from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from entity.base import Base
from entity.sensor import Sensor


class Pet(Base):
    __tablename__ = 'pet'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)


class PetHabitat(Base):
    __tablename__ = 'pet_habitat'
    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey('pet.id'))
    information = Column(JSON)
    pet = relationship("Pet", back_populates="habitat")
