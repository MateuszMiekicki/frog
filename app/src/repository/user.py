from entity import user as entity
from sqlalchemy.orm import Session
from configure.database import Database


class User():
    def __init__(self, database: Database):

        self.database = database

    def add_user(self, email: str, password: str, role: str):
        with self.database.get_db() as db:
            role_id = db.query(entity.Role.id).filter(
                entity.Role.role == role).scalar()
            new_user = entity.User(
                email=email, password=password, role_id=role_id)
            db.add(new_user)
            db.commit()

    def get_user(self, email: str):
        with self.database.get_db() as db:
            return db.query(entity.User).filter(entity.User.email == email).first()
        raise Exception("todo: error")

    def is_user_exist(self, email: str) -> bool:
        return self.get_user(email) is not None
