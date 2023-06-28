from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from typing import Optional
from enum import Enum
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from fastapi import APIRouter, status, Request, HTTPException, Security
import logging


class Dialect(Enum):
    postgresql = 'postgresql'


class Driver(Enum):
    none = ''


class DatabaseAuth:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def get_auth(self):
        return f'{self.username}:{self.password}'


class DatabaseAddress:
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port

    def get_address(self):
        return f'{self.address}:{self.port}'


class Database:
    def __create_address(self, dialect: Dialect, driver: Driver,
                         address: DatabaseAddress, database: str,
                         auth: DatabaseAuth):
        if driver is not Driver.none:
            driver = f'+{driver.value}'
        else:
            driver = ''
        return f'{dialect.value}{driver}://{auth.get_auth()}@{address.get_address()}/{database}'

    def __create_engine(self, url: str):
        return create_engine(url, pool_pre_ping=True)

    def __check_connection(self, engine):
        try:
            engine.connect()
        except Exception as error:
            logging.error(error)
            raise

    def __make_session(self, engine):
        return sessionmaker(expire_on_commit=False, autocommit=False, autoflush=False, bind=engine)

    def connect(self, dialect: Dialect, driver: Driver,
                address: DatabaseAddress, database: str,
                auth: DatabaseAuth):
        url = self.__create_address(dialect, driver, address, database, auth)
        engine = self.__create_engine(url)
        self.__check_connection(engine)
        self.session_local = self.__make_session(engine)

    @contextmanager
    def get_db(self):
        db = self.session_local()
        try:
            yield db
            db.commit()
        except Exception as error:
            logging.error('Error during transaction: ', error)
            db.rollback()
            raise
        finally:
            db.expunge_all()
            db.close()
