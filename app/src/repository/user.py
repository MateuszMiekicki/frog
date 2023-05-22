from entity import user as entity
from sqlalchemy.orm import Session
from configuration.database import Database
from sqlalchemy import func


class User():
    def __init__(self, database: Database):
        self.database = database

    def __get_id_by_role(self, role: str) -> int:
        with self.database.get_db() as db:
            return db.query(entity.Role.id).filter(entity.Role.role == role).scalar()

    def add_user(self, email: str, password: str, role: str):
        with self.database.get_db() as db:
            new_user = entity.User(
                email=email, password=password, role_id=self.__get_id_by_role(role))
            db.add(new_user)
            db.commit()

    def get_user(self, email: str):
        with self.database.get_db() as db:
            return db.query(entity.User).filter(func.lower(entity.User.email) == func.lower(email)).first()
        raise Exception('todo: error')

    def is_user_exist(self, email: str) -> bool:
        return self.get_user(email) is not None
