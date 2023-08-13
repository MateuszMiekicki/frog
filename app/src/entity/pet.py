from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from entity.base import Base
from entity.sensor import Sensor


class Pet(Base):
    __tablename__ = 'pet'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    habitat = relationship("PetHabitat", back_populates="pet")


class PetHabitat(Base):
    __tablename__ = 'pet_habitat'
    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey('pet.id'), nullable=False)
    information = Column(JSON)

    pet = relationship("Pet", back_populates="habitat")
