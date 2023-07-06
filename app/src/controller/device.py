from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import repository.device as deviceRepository
import repository.sensor as sensorRepository
from controller.dto.device import Device
import zmq
import time
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def __trim_mac_address(mac_address):
    return mac_address.replace(' ', '')


def __cast_to_lower_case(mac_address):
    return mac_address.lower()


def prepare_mac_address_to_add_to_database(mac_address):
    return __cast_to_lower_case(__trim_mac_address(mac_address))


def send_request(receiver_address: str, client_id: str, request: str):
    context = zmq.Context()

    client = context.socket(zmq.DEALER)
    client.setsockopt(zmq.RCVBUF, 1000000)
    client.identity = client_id.encode()
    client.connect(receiver_address)
    poller = zmq.Poller()
    poller.register(client, zmq.POLLIN)
    client.send(request.encode())

    timeout = 10000
    if poller.poll(timeout):
        # set buffer size to 1MB
        response = client.recv()

        client.close()
        context.term()
        return "resp: "+response.decode()
    else:
        client.close()
        context.term()
        # raise TimeoutError("Connection timed out")
        return "Connection timed out"


def __prepare_information_about_devices_with_sensors(devices, sensors):
    if sensors is None:
        return {'id': devices.id, 'name': devices.name, 'mac_address': devices.mac_address, 'sensors': []}
    return {'id': devices.id, 'name': devices.name, 'mac_address': devices.mac_address, 'sensors': [{'id': sensor.id, 'name': sensor.name, 'pin_number': sensor.pin_number, 'type': sensor.type, 'min_value': sensor.min_value, 'max_value': sensor.max_value} for sensor in sensors]}


@router.post('/device', status_code=status.HTTP_201_CREATED)
async def add_device(request: Request, device: Device, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    repo = deviceRepository.Device(request.app.state.postgresql)
    if repo.get_device_by_mac_address(device.mac_address):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'The device with the mac_address {device.mac_address} is already in the database.')
    repo.add_device(decoded_token.get('sub'), device.name,
                    prepare_mac_address_to_add_to_database(device.mac_address))
    return {'detail': f'device with mac address: {device.mac_address} added'}


@router.get('/devices', status_code=status.HTTP_200_OK)
async def get_devices(request: Request, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    repo = deviceRepository.Device(request.app.state.postgresql)
    return repo.get_devices_by_user_id(decoded_token.get('sub'))


@router.get('/device/{device_id}', status_code=status.HTTP_200_OK)
async def get_devices(request: Request, device_id: int, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    database = request.app.state.postgresql
    repo = deviceRepository.Device(database)
    device = repo.get_device_by_id(device_id)
    logging.info(f"is exist device: {device is not None}")
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The device with the id {device_id} was not found.')
    if device.user_id != decoded_token.get('sub'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'The device with the id {device_id} is not owned by you.')
    logging.info(f"device: {device_id}")
    sensors = sensorRepository.Sensor(
        database).get_sensors_assigned_to_device(device_id)
    return __prepare_information_about_devices_with_sensors(device, sensors)


@router.delete('/device/{device_id}', status_code=status.HTTP_200_OK)
def delete_device(request: Request, device_id: int, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    repo = deviceRepository.Device(request.app.state.postgresql)
    device = repo.get_device_by_id(device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The device with the id {device_id} was not found.')
    if device.user_id != decoded_token.get('sub'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'The device with the id {device_id} is not owned by you.')
    repo.delete_device(device_id)
    return {'detail': f'device with id {device_id} deleted'}


@router.get('/device/{device_id}/configuration', status_code=status.HTTP_200_OK)
def get_device_configuration(request: Request, device_id: int):
    # decoded_token = request.app.state.authenticate.decode_token(token)
    # repo = deviceRepository.Device(request.app.state.postgresql)
    # device = repo.get_device_by_id(device_id)
    # if device is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f'The device with the id {device_id} was not found.')
    # if device.user_id != decoded_token.get('sub'):
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                         detail=f'The device with the id {device_id} is not owned by you.')
    response = send_request("tcp://localhost:5570", "client1",
                            f"get configuration from device {device_id}")
    return {'detail': f'configuration for device {response}'}
