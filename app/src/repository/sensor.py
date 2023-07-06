from entity import device as entity
from sqlalchemy.orm import Session
from configuration.database import Database


class Sensor():
    def __init__(self, database: Database):
        self.database = database

    def add_sensor(self, device_id: int, name: str, pin_number: int, type: str, min_value: float, max_value: float):
        with self.database.get_db() as db:
            new_sensor = entity.Sensor(
                device_id=device_id, name=name, pin_number=pin_number, type=type,  min_value=min_value, max_value=max_value)
            db.add(new_sensor)
            db.commit()

    def get_sensor_assigned_to_device_pin_number(self, device_id: int, pin_number: int):
        with self.database.get_db() as db:
            return db.query(entity.Sensor).filter(entity.Sensor.device_id == device_id,
                                                  entity.Sensor.pin_number == pin_number).first()

    def get_sensors_assigned_to_device(self, device_id: int):
        with self.database.get_db() as db:
            return db.query(entity.Sensor).filter(entity.Sensor.device_id == device_id).all()
    # def get_device_by_id(self, device_id: int):
    #     with self.database.get_db() as db:
    #         return db.query(entity.Device).filter(entity.Device.id == device_id).first()
    #     raise Exception('todo: error')

    # def get_device_by_key(self, key: str):
    #     with self.database.get_db() as db:
    #         return db.query(entity.Device).filter(entity.Device.key == key).first()
    #     raise Exception('todo: error')

    # def get_devices(self, user_id: int):
    #     with self.database.get_db() as db:
    #         return db.query(entity.Device).filter(entity.Device.user_id == user_id).all()
    #     raise Exception('todo: error')

    # def delete_device(self, device_id: int):
    #     with self.database.get_db() as db:
    #         db.query(entity.Device).filter(
    #             entity.Device.id == device_id).delete()
    #         db.commit()
