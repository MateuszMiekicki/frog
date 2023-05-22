from security import hashing
from controller.dto.user import User
import repository.user as repository


def add_user(database, user):
    database = repository.User(database)
    if database.is_user_exist(user.email):
        return False
    database.add_user(email=user.email,
                      password=hashing.hash(user.password.get_secret_value()),
                      role='owner')
    return True


def verify_user(database, user):
    database = repository.User(database)
    user_from_db = database.get_user(user.email)
    if user_from_db and hashing.verify(user_from_db.password, user.password.get_secret_value()):
        return user_from_db
    return None
