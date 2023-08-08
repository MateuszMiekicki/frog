import pytest
import requests
import json
from datetime import datetime
import database_helper as db_helper


class LoginFixture:
    def __create_user_name_base_on_time(self):
        return datetime.now().strftime("%Y%m%d%H%M%S") + "@gmail.com"

    def __init__(self):
        self.email = self.__create_user_name_base_on_time()
        self.endpoint = "http://localhost:8000"
        self.db_helper = db_helper.DatabaseHelper()

    def add_active_user(self, email, password):
        self.db_helper.add_active_user(email, password)

    def get_email(self):
        return self.email

    def get_password(self):
        return "123456"

    def get_endpoint(self):
        return self.endpoint


@pytest.fixture(scope='session', autouse=True)
def create_fixture():
    login_fixture = LoginFixture()

    login_fixture.add_active_user(
        login_fixture.get_email(), login_fixture.get_password())
    return login_fixture


def test_login(create_fixture):
    payload = {
        "email": create_fixture.get_email(),
        "password": create_fixture.get_password(),
    }
    response = requests.post(
        create_fixture.get_endpoint()+"/login", json=payload
    )
    assert response.status_code == requests.codes.ok


def test_login_with_wrong_password(create_fixture):
    payload = {
        "email": create_fixture.get_email(),
        "password": "wrong_password",
    }
    response = requests.post(
        create_fixture.get_endpoint()+"/login", json=payload
    )
    assert response.status_code == requests.codes.unauthorized
