import pytest
import database_helper as db_helper
import requests
from datetime import datetime
import uuid
import json


class DeviceFixture:
    def __create_user_name_base_on_time(self):
        return "test@gmail.com"

    def __init__(self):
        self.endpoint = "http://localhost:8000"
        self.db_helper = db_helper.DatabaseHelper()
        self.email = self.__create_user_name_base_on_time()
        self.password = "123456"

    def get_endpoint(self):
        return self.endpoint

    def add_active_user(self):
        pass
        # self.db_helper.add_active_user(self.email, self.password)

    def login(self):
        payload = {
            "email": self.email,
            "password": self.password,
        }
        response = requests.post(
            self.get_endpoint()+"/login", json=payload
        )
        assert response.status_code == requests.codes.ok
        return response.json()['access_token']

    def generate_random_mac_address(self):
        return str(uuid.uuid4())


@pytest.fixture(scope='session', autouse=True)
def create_fixture():
    device_fixture = DeviceFixture()
    device_fixture.add_active_user()
    return device_fixture


def test_add_new_device(create_fixture):
    token = create_fixture.login()
    mac_address = create_fixture.generate_random_mac_address()
    print(mac_address)
    payload = {
        'mac_address': f'{mac_address}',
        'name': 'test_device'
    }

    response = requests.post(
        create_fixture.get_endpoint()+"/device", json=payload, headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == requests.codes.created


def test_get_devices_list(create_fixture):
    token = create_fixture.login()

    response = requests.get(
        create_fixture.get_endpoint()+"/devices", headers={'Authorization': f'Bearer {token}'}
    )
    response_json = response.json()
    assert response_json is not None
    assert response.status_code == requests.codes.ok


def test_get_configuration(create_fixture):
    token = create_fixture.login()

    devices = requests.get(
        create_fixture.endpoint+"/devices", headers={'Authorization': f'Bearer {token}'}
    ).json()

    device_id = devices[0]['id']

    response = requests.get(
        create_fixture.get_endpoint()+f"/device/{device_id}/configuration", headers={'Authorization': f'Bearer {token}'}
    )
    print(response.json())
    assert response.status_code == requests.codes.ok
