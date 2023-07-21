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


class ConfigForRequest():
    # todo: move context to request app state
    context = zmq.Context()

    def __init__(self, receiver_address: str, timeout: int):
        self.receiver_address = receiver_address
        self.timeout = timeout

    def get_receiver_address(self):
        return self.receiver_address

    def get_timeout(self):
        return self.timeout


async def send_request(client_id: str, request: str, zmq_config: ConfigForRequest):
    client = zmq_config.context.socket(zmq.DEALER)
    client.identity = client_id.encode()
    client.connect(zmq_config.get_receiver_address())
    poller = zmq.Poller()
    poller.register(client, zmq.POLLIN)
    client.send(request.encode())
    logging.debug(f"from {client_id} send request: {request}")
    if poller.poll(zmq_config.get_timeout()):
        response = client.recv()
        client.close()
        # zmq_config.context.term()
        logging.trace(f"response: {response}")
        return [status.HTTP_200_OK, response.decode()]

    logging.debug("No response from server - timeout")
    client.close()
    # zmq_config.context.term()
    return [status.HTTP_408_REQUEST_TIMEOUT, "Connection timed out"]


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
async def delete_device(request: Request, device_id: int, token: str = Depends(oauth2_scheme)):
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

# todo: move to request state context
zmq_config = ConfigForRequest("tcp://localhost:5571", 10000)


@router.get('/device/{device_id}/configuration', status_code=status.HTTP_200_OK)
async def get_device_configuration(request: Request, device_id: int):
    ret = await send_request("test", "get_config", zmq_config)
    raise HTTPException(status_code=ret[0], detail=ret[1])


@router.post('/device/{device_id}/configuration', status_code=status.HTTP_200_OK)
async def set_device_configuration(request: Request, device_id: int):
    print(await request.json())
    ret = await send_request("test", "set_config", zmq_config)
    raise HTTPException(status_code=ret[0], detail=ret[1])
