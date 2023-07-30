from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import repository.sensor as sensor_repository
import repository.device as device_repository
from controller.dto.sensor import Sensor
from controller.facade import device_checker

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.post('/device/{device_id}/sensor', status_code=status.HTTP_201_CREATED)
async def add_sensor(request: Request, device_id: int, sensor: Sensor, token: str = Depends(oauth2_scheme)):
    user_id = request.app.state.authenticate.decode_token(token).get('sub')

    repo = device_repository.Device(request.app.state.postgresql)
    device = repo.get_device_by_id(device_id)
    device_checker.is_device_exists(device, device_id)
    device_checker.is_device_owned_by_user(device, user_id)

    repo = sensor_repository.Sensor(request.app.state.postgresql)
    if repo.get_sensor_assigned_to_device_pin_number(device_id, sensor.pin_number) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'The pin {sensor.pin_number} is already associated with device id {device_id}.')
    repo.add_sensor(device_id, sensor.name, sensor.pin_number,
                    sensor.type, sensor.min_value, sensor.max_value)
    return {'detail': 'sensor is associated with a device'}


@router.get('/device/{device_id}/sensor', status_code=status.HTTP_200_OK)
async def get_sensors(request: Request, device_id: int, token: str = Depends(oauth2_scheme)):
    user_id = request.app.state.authenticate.decode_token(token).get('sub')

    device_repo = device_repository.Device(request.app.state.postgresql)
    device = device_repo.get_device_by_id(device_id)
    device_checker.is_device_exists(device, device_id)
    device_checker.is_device_owned_by_user(device, user_id)

    sensor_repo = sensor_repository.Sensor(request.app.state.postgresql)
    sensors = sensor_repo.get_sensors_assigned_to_device(device_id)

    return [{'id': sensor.id, 'name': sensor.name, 'pin_number': sensor.pin_number, 'type': sensor.type, 'min_value': sensor.min_value, 'max_value': sensor.max_value} for sensor in sensors]


@router.delete('/device/{device_id}/sensor/{sensor_id}', status_code=status.HTTP_200_OK)
async def delete_sensor(request: Request, device_id: int, sensor_id: int, token: str = Depends(oauth2_scheme)):
    user_id = request.app.state.authenticate.decode_token(token).get('sub')

    device_repo = device_repository.Device(request.app.state.postgresql)
    device = device_repo.get_device_by_id(device_id)
    device_checker.is_device_exists(device, device_id)
    device_checker.is_device_owned_by_user(device, user_id)

    sensor_repo = sensor_repository.Sensor(request.app.state.postgresql)
    sensor = sensor_repo.get_sensor_by_id(sensor_id)
    if sensor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The sensor with the id {sensor_id} was not found.')
    if sensor.device_id != device_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'The sensor with the id {sensor_id} is not associated with device id {device_id}.')
    sensor_repo.delete_sensor(sensor_id)
    return {'detail': f'sensor with id {sensor_id} deleted'}


@router.put('/device/{device_id}/sensor/{sensor_id}', status_code=status.HTTP_200_OK)
async def update_sensor(request: Request, device_id: int, sensor_id: int, sensor: Sensor, token: str = Depends(oauth2_scheme)):
    user_id = request.app.state.authenticate.decode_token(token).get('sub')

    device_repo = device_repository.Device(request.app.state.postgresql)
    device = device_repo.get_device_by_id(device_id)
    device_checker.is_device_exists(device, device_id)
    device_checker.is_device_owned_by_user(device, user_id)

    sensor_repo = sensor_repository.Sensor(request.app.state.postgresql)
    sensor_to_update = sensor_repo.get_sensor_by_id(sensor_id)
    if sensor_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The sensor with the id {sensor_id} was not found.')
    if sensor_to_update.device_id != device_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'The sensor with the id {sensor_id} is not associated with device id {device_id}.')

    def dto_sensor_to_entity(sensor_id: int, sensor: Sensor):
        return sensor_repository.entity.Sensor(id=sensor_id, device_id=device_id, name=sensor.name, pin_number=sensor.pin_number, type=sensor.type, min_value=sensor.min_value, max_value=sensor.max_value)

    sensor_repo.update_sensor(dto_sensor_to_entity(sensor_id, sensor))
    return {'detail': f'sensor with id {sensor_id} updated'}


@router.put('/device/{device_id}/sensor', status_code=status.HTTP_200_OK)
async def update_sensors(request: Request, device_id: int, sensors: list[Sensor], token: str = Depends(oauth2_scheme)):
    user_id = request.app.state.authenticate.decode_token(token).get('sub')

    device_repo = device_repository.Device(request.app.state.postgresql)
    device = device_repo.get_device_by_id(device_id)
    device_checker.is_device_exists(device, device_id)
    device_checker.is_device_owned_by_user(device, user_id)

    sensor_repo = sensor_repository.Sensor(request.app.state.postgresql)
    sensors_to_update = sensor_repo.get_sensors_assigned_to_device(device_id)
    if len(sensors_to_update) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'There are no sensors associated with device id {device_id}.')
    if len(sensors_to_update) != len(sensors):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'The number of sensors to update is not equal to the number of sensors associated with device id {device_id}.')

    def dto_sensor_to_entity(sensor_id: int, sensor: Sensor):
        return sensor_repository.entity.Sensor(id=sensor_id, device_id=device_id, name=sensor.name, pin_number=sensor.pin_number, type=sensor.type, min_value=sensor.min_value, max_value=sensor.max_value)

    for sensor in sensors:
        sensor_to_update = next(
            (sensor_to_update for sensor_to_update in sensors_to_update if sensor_to_update.pin_number == sensor.pin_number), None)
        if sensor_to_update is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'The sensor with the pin number {sensor.pin_number} was not found.')
        sensor_repo.update_sensor(
            dto_sensor_to_entity(sensor_to_update.id, sensor))
    return {'detail': f'sensors with pin numbers {", ".join([str(sensor.pin_number) for sensor in sensors])} updated'}
