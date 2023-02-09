# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from entity import user as entity
# from contextlib import contextmanager

# engine = create_engine('postgresql://frog:frog!123@127.0.0.1:5400/frog')
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# @contextmanager
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#         db.commit()
#     except Exception:
#         db.rollback()
#         raise
#     finally:
#         db.close()


# def add_user(email: str, password: str, role: str):
#     with get_db() as db:
#         role_id = db.query(entity.Role.id).filter(
#             entity.Role.role == role).scalar()
#         new_user = entity.User(email=email, password=password, role_id=role_id)
#         db.add(new_user)
#         db.commit()


# def get_user(email: str):
#     with get_db() as db:
#         return db.query(entity.User).filter(entity.User.email == email).first()


# def is_user_exist(email: str) -> bool:
#     with get_db() as db:
#         return get_user(email) is not None
#     raise Exception("todo: error")


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
            new_user = entity.User(email=email, password=password, role_id=role_id)
            db.add(new_user)
            db.commit()


    def get_user(self, email: str):
        with self.database.get_db() as db:
            return db.query(entity.User).filter(entity.User.email == email).first()
        raise Exception("todo: error")


    def is_user_exist(self, email: str) -> bool:
        return self.get_user(email) is not None