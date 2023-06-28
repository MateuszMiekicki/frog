from entity import user as entity
from sqlalchemy.orm import Session
from configuration.database import Database
from sqlalchemy import func


class User():
    def __init__(self, database: Database):
        self.database = database

    def add_user(self, email: str, password: str):
        with self.database.get_db() as db:
            new_user = entity.User(
                email=email, password=password)
            db.add(new_user)
            db.commit()
            return new_user

    def get_user(self, email: str):
        with self.database.get_db() as db:
            result = db.query(entity.User).filter(func.lower(
                entity.User.email) == func.lower(email)).first()
            db.commit()
            return result

    def is_user_exist(self, email: str) -> bool:
        return self.get_user(email) is not None

    def change_active_status(self, user_id: int, is_active: bool):
        with self.database.get_db() as db:
            db.query(entity.User).filter(
                entity.User.id == user_id).update({entity.User.is_active: is_active})
            db.commit()

    def change_password(self, user_id: int, password: str):
        with self.database.get_db() as db:
            db.query(entity.User).filter(
                entity.User.id == user_id).update({entity.User.password: password})
            db.commit()
