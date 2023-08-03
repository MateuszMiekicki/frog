from sqlalchemy import Column, Integer, String, Boolean
from entity.base import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)

    devices = relationship('Device', back_populates='user',
                           cascade='all, delete-orphan')
