from sqlalchemy import Column, Integer, String, Boolean
from entity.base import Base
from sqlalchemy.orm import relationship
from entity.user import User


class Visitor(Base):
    __tablename__ = 'visitor'
    user = relationship('User')
    device = relationship('Device')

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    device_id = Column(Integer, nullable=False)
    name = Column(String)
