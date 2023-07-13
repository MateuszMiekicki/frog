from entity import alert as entity
from sqlalchemy.orm import Session
from configuration.database import Database


class Alert():
    def __init__(self, database: Database):
        self.database = database

    def add_alert(self, device_id: int, sensor_id: int, date: str, description: str, served: bool = False):
        with self.database.get_db() as db:
            new_alert = entity.Alert(
                device_id=device_id, sensor_id=sensor_id, date=date, description=description, served=served)
            db.add(new_alert)
            db.commit()

    def get_alerts_by_device_id(self, device_id: int):
        with self.database.get_db() as db:
            return db.query(entity.Alert).filter(entity.Alert.device_id == device_id).all()

    def get_not_served_alerts_by_device_id(self, device_id: int):
        with self.database.get_db() as db:
            return db.query(entity.Alert).filter(entity.Alert.device_id == device_id, entity.Alert.served == False).all()

    def get_alert_by_id(self, alert_id: int):
        with self.database.get_db() as db:
            return db.query(entity.Alert).filter(entity.Alert.id == alert_id).first()

    def serve_alert(self, alert_id: int):
        with self.database.get_db() as db:
            alert = db.query(entity.Alert).filter(
                entity.Alert.id == alert_id).first()
            alert.served = True
            db.commit()

    def delete_alert(self, alert_id: int):
        with self.database.get_db() as db:
            alert = db.query(entity.Alert).filter(
                entity.Alert.id == alert_id).first()
            db.delete(alert)
            db.commit()

    def get_alerts_with_parameters(self,
                                   device_id: int,
                                   skip: int = 0,
                                   limit: int = 10,
                                   sort_by_priority: bool = False,
                                   sort_by_date: bool = False,
                                   only_served: bool = False,
                                   only_not_served: bool = False):
        with self.database.get_db() as db:
            alerts = db.query(entity.Alert).filter(
                entity.Alert.device_id == device_id).all()
            if only_served:
                alerts = list(filter(lambda alert: alert.served, alerts))
            if only_not_served:
                alerts = list(filter(lambda alert: not alert.served, alerts))
            if sort_by_priority:
                alerts = sorted(
                    alerts, key=lambda alert: alert.priority, reverse=True)
            if sort_by_date:
                alerts = sorted(
                    alerts, key=lambda alert: alert.date, reverse=True)
            return alerts[skip:skip+limit]
