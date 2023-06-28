from entity import user, user_confirmation as entity
from sqlalchemy.orm import Session
from configuration.database import Database
from sqlalchemy import func


class UserConfirmation():
    def __init__(self, database: Database):
        self.database = database

    def add_user_confirmation_code(self, user_id: int, confirmation_code: str):
        with self.database.get_db() as db:
            new_user_confirmation = entity.UserConfirmation(
                user_id=user_id, confirmation_code=confirmation_code)
            db.add(new_user_confirmation)
            db.commit()

    def get_by_confirmation_code(self, key: str) -> entity.UserConfirmation:
        with self.database.get_db() as db:
            result = db.query(entity.UserConfirmation).filter(
                entity.UserConfirmation.confirmation_code == key).first()
            db.commit()
            return result

    def delete_confirmation_code(self, key: str):
        with self.database.get_db() as db:
            db.query(entity.UserConfirmation).filter(
                entity.UserConfirmation.confirmation_code == key).delete()
            db.commit()
