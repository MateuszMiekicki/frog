from entity import device as entity
from sqlalchemy.orm import Session
from configure.database import Database


class Device():
    def __init__(self, database: Database):

        self.database = database

    def add_device(self, user_id: int, name: str, key: str):
        with self.database.get_db() as db:
            new_device = entity.Device(user_id=user_id, name=name, key=key)
            db.add(new_device)
            db.commit()

    def get_device(self, device_id: int):
        with self.database.get_db() as db:
            return db.query(entity.Device).filter(entity.Device.id == device_id).first()
        raise Exception("todo: error")

    def get_devices(self, user_id: int):
        with self.database.get_db() as db:
            return db.query(entity.Device)
        raise Exception("todo: error")
