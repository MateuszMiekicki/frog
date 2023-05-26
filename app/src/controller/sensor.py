from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import repository.sensor as sensor_repository
import repository.device as device_repository
from controller.dto.sensor import Sensor

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.post('/device/sensor', status_code=status.HTTP_201_CREATED)
async def read_users_me(request: Request, sensor: Sensor, token: str = Depends(oauth2_scheme)):
    request.app.state.authenticate.decode_token(token)
    repo = device_repository.Device(request.app.state.postgresql)
    device = repo.get_device_by_id(sensor.device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The device with the id {sensor.device_id} was not found.')
    if device.user_id != request.app.state.authenticate.decode_token(token).get('sub'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'The device with the id {sensor.device_id} is not owned by you.')
    repo = sensor_repository.Sensor(request.app.state.postgresql)
    repo.add_sensor(sensor.device_id, sensor.name, sensor.pin,
                    sensor.type, sensor.min_value, sensor.max_value)

    return {'detail': 'sensor is associated with a device'}
