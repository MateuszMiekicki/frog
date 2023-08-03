from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey
from entity.base import Base
from sqlalchemy.orm import relationship
from entity.user import User


class UserConfirmation(Base):
    __tablename__ = 'user_confirmation'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)
    confirmation_code = Column(String, nullable=False)
