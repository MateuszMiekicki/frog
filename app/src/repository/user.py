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

    def get_user(self, email: str):
        with self.database.get_db() as db:
            return db.query(entity.User).filter(func.lower(entity.User.email) == func.lower(email)).first()
        raise Exception('todo: error')

    def is_user_exist(self, email: str) -> bool:
        return self.get_user(email) is not None
