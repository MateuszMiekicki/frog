from src.configuration.configuration import PostgreSQLConfiguration
import mock
import pytest

CONFIG = '''databases:
    postgresql:
        hostname: ${FROG_DATABASE_ADDRESS:postgresql}
        port: ${FROG_DATABASE_PORT:5432}
        database_name: ${FROG_DATABASE_DB_NAME:frog}
        user_name: ${FROG_DATABASE_USER:frog}
        password: ${FROG_DATABASE_PASSWORD:frog!123}
    questdb:
        hostname: ${FROG_DATABASE_ADDRESS:questdb}
        port: ${FROG_DATABASE_PORT:5400}
        database_name: ${FROG_DATABASE_DB_NAME:frog}
        user_name: ${FROG_DATABASE_USER:frog}
        password: ${FROG_DATABASE_PASSWORD:frog!123}
'''


def test_get_from_config_port_for_postgresql():
    frog = PostgreSQLConfiguration(CONFIG)
    assert frog.get_port() == 5432


def test_get_from_config_hostname_for_postgresql():
    frog = PostgreSQLConfiguration(CONFIG)
    assert frog.get_hostname() == 'postgresql'


def test_get_from_config_password_for_postgresql():
    frog = PostgreSQLConfiguration(CONFIG)
    assert frog.get_password() == 'frog!123'


def test_get_from_config_database_name_for_postgresql():
    frog = PostgreSQLConfiguration(CONFIG)
    assert frog.get_database_name() == 'frog'


def test_get_from_config_user_for_postgresql():
    frog = PostgreSQLConfiguration(CONFIG)
    assert frog.get_user_name() == 'frog'
