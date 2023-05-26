from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import repository.device as repository
from controller.dto.device import Sensor

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.post('/device/sensor', status_code=status.HTTP_201_CREATED)
async def read_users_me(request: Request, device: Sensor, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    repo = repository.Device(request.app.state.postgresql)
    if repo.get_device_by_key(device.key):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'The device with the key {device.key} is already in the database.')
    repo.add_device(decoded_token.get('sub'), device.name, device.key)
    return {'detail': 'device created'}
