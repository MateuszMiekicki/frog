import pytest
import requests
import json
from datetime import datetime
import time
import database_helper as db_helper


class RegisterFixture:
    def __create_user_name_base_on_time(self):
        return datetime.now().strftime("%Y%m%d%H%M%S") + "@gmail.com"

    def __init__(self):
        self.email = self.__create_user_name_base_on_time()
        self.endpoint = "http://localhost:8000"
        self.db_helper = db_helper.DatabaseHelper()

    def get_email(self):
        return self.email

    def get_endpoint(self):
        return self.endpoint


@pytest.fixture(scope='session', autouse=True)
def create_fixture():
    return RegisterFixture()


def test_create_new_user(create_fixture):
    payload = {
        "email": create_fixture.get_email(),
        "password": "123456",
    }
    response = requests.post(
        create_fixture.get_endpoint()+"/register", json=payload
    )

    assert response.status_code == requests.codes.created


def test_create_new_user_with_existing_email(create_fixture):
    payload = {
        "email": create_fixture.get_email(),
        "password": "123456",
    }
    response = requests.post(
        create_fixture.get_endpoint()+"/register", json=payload
    )

    assert response.status_code == requests.codes.conflict


def test_confirm_registration():
    reqgister_fixture = RegisterFixture()

    payload = {
        "email": reqgister_fixture.get_email(),
        "password": "123456",
    }
    response = requests.post(
        reqgister_fixture.get_endpoint()+"/register", json=payload
    )

    assert response.status_code == requests.codes.created

    active_code = reqgister_fixture.db_helper.get_active_code(
        reqgister_fixture.get_email()
    )
    response = requests.get(
        reqgister_fixture.get_endpoint()+"/register/"+active_code
    )

    assert response.status_code == requests.codes.accepted
