from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from entity import user as entity

engine = create_engine('postgresql://frog:frog!123@127.0.0.1:5400/frog')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from contextlib import contextmanager

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def add_user(email: str, password: str, role: str):
    with get_db() as db:
        # role_id = db.query(entity.role.Role.id).filter(entity.role.Role.role == role).scalar()
        new_user = entity.User(email=email, password=password, role_id=2)
        db.add(new_user)
        db.commit()

def get_user(email: str):
    with get_db() as db:
        return db.query(User).filter(User.email == email).first()