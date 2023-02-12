from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
# from entity.device import Device

from entity.base import Base
class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    role = Column(String, unique=True, nullable=False)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = relationship("Role", back_populates="users")


Role.users = relationship("User", order_by=User.id, back_populates="role")
# User.devices = relationship(
#     "Device", order_by=Device.id, back_populates="device")
