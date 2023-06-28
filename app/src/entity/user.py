from sqlalchemy import Column, Integer, String, Boolean
from entity.base import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'
    user_confirmation_codes = relationship(
        'UserConfirmation', cascade="all, delete-orphan")

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
