from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import repository.sensor as sensor_repository
import repository.device as device_repository
from controller.dto.sensor import Sensor
from controller.facade import device_checker

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.post('/device/sensor', status_code=status.HTTP_201_CREATED)
async def read_users_me(request: Request, sensor: Sensor, token: str = Depends(oauth2_scheme)):
    user_id = request.app.state.authenticate.decode_token(token).get('sub')

    repo = device_repository.Device(request.app.state.postgresql)
    devices = repo.get_devices(user_id)
    if len(devices) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'There are no devices associated with user id {user_id}.')
    if len(devices) > 1 and sensor.device_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'There are more than one device associated with user id {user_id}. Please specify the device id.')
    if len(devices) == 1:
        sensor.device_id = devices[0].id
    device = repo.get_device_by_id(sensor.device_id)
    device_checker.is_device_exists(device, sensor.device_id)
    device_checker.is_device_owned_by_user(device, user_id)

    repo = sensor_repository.Sensor(request.app.state.postgresql)
    if repo.get_sensor_assigned_to_device_pin(sensor.device_id, sensor.pin) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'The pin {sensor.pin} is already associated with device id {sensor.device_id}.')
    repo.add_sensor(sensor.device_id, sensor.name, sensor.pin,
                    sensor.type, sensor.min_value, sensor.max_value)
    return {'detail': 'sensor is associated with a device'}
