from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


from entity.base import Base

class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    key = Column(String, nullable=False, unique=True)
    name = Column(String)
