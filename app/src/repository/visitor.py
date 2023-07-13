from entity import visitor as entity
from sqlalchemy.orm import Session
from configuration.database import Database
from sqlalchemy import func


class Visitor():
    def __init__(self, database: Database):
        self.database = database

    def assign_visitor_to_device(self, user_id: int, device_id: int, name: str = None):
        with self.database.get_db() as db:
            new_visitor = entity.Visitor(
                user_id=user_id, device_id=device_id, name=name)
            db.add(new_visitor)
            db.commit()
            return new_visitor

    def get_visitor_by_id(self, visitor_id: int):
        with self.database.get_db() as db:
            result = db.query(entity.Visitor).filter(
                entity.Visitor.id == visitor_id).first()
            db.commit()
            return result

    def get_visitors(self, device_id: int):
        with self.database.get_db() as db:
            result = db.query(entity.Visitor).filter(
                entity.Visitor.device_id == device_id).all()
            db.commit()
            return result

    def remove_visitor(self, visitor_id: int):
        with self.database.get_db() as db:
            db.query(entity.Visitor).filter(
                entity.Visitor.id == visitor_id).delete()
            db.commit()
