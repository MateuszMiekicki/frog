from entity import device as entity
from sqlalchemy.orm import Session
from configuration.database import Database


class Device():
    def __init__(self, database: Database):

        self.database = database

    def add_device(self, user_id: int, name: str, key: str):
        with self.database.get_db() as db:
            new_device = entity.Device(user_id=user_id, name=name, key=key)
            db.add(new_device)
            db.commit()

    def get_device_by_id(self, device_id: int):
        with self.database.get_db() as db:
            return db.query(entity.Device).filter(entity.Device.id == device_id).first()
        raise Exception('todo: error')

    def get_device_by_key(self, key: str):
        with self.database.get_db() as db:
            return db.query(entity.Device).filter(entity.Device.key == key).first()
        raise Exception('todo: error')

    def get_devices(self, user_id: int):
        with self.database.get_db() as db:
            return db.query(entity.Device).filter(entity.Device.user_id == user_id).all()
        raise Exception('todo: error')
