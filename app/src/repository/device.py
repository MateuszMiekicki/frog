from entity import device as entity
from sqlalchemy.orm import Session
from configuration.database import Database
from sqlalchemy.orm import joinedload


class Device():
    def __init__(self, database: Database):
        self.database = database

    def add_device(self, user_id: int, name: str, mac_address: str):
        with self.database.get_db() as db:
            new_device = entity.Device(
                user_id=user_id, name=name, mac_address=mac_address)
            db.add(new_device)
            db.commit()

    def get_device_by_id(self, device_id: int):
        with self.database.get_db() as db:
            return db.query(entity.Device).filter(entity.Device.id == device_id).first()

    def get_device_by_mac_address(self, mac_address: str):
        with self.database.get_db() as db:
            return db.query(entity.Device).filter(entity.Device.mac_address == mac_address).first()

    def get_devices_by_user_id(self, user_id: int):
        with self.database.get_db() as db:
            return db.query(entity.Device).filter(entity.Device.user_id == user_id).all()

    def delete_device(self, device_id: int):
        with self.database.get_db() as db:
            # device = db.query(entity.Device).options(
            #     joinedload(entity.Device.sensors),
            #     joinedload(entity.Device.alerts)
            # ).filter(entity.Device.id == device_id).first()

            # if device:
            #     for alert in device.alerts:
            #         db.delete(alert)

            #     for sensor in device.sensors:
            #         db.delete(sensor)

            #     db.delete(device)
            #     db.commit()
            device = db.query(entity.Device).filter(
                entity.Device.id == device_id).first()
            db.delete(device)
            db.commit()
