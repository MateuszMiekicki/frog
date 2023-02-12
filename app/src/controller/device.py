from security import hashing
from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import repository.device as repository
from dto.device import Device
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.post('/device', status_code=status.HTTP_201_CREATED)
async def read_users_me(request: Request, device: Device, token: str = Depends(oauth2_scheme)):
    decode_token = request.app.state.authenticate.decode_token(token)
    repo = repository.Device(request.app.state.database)
    if repo.get_device_by_key(device.key):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'The device with the key {device.key} is already in the database.')
    repo.add_device(decode_token.get('sub'), device.name, device.key)


@router.get('/devices', status_code=status.HTTP_200_OK)
async def read_users_me(request: Request, token: str = Depends(oauth2_scheme)):
    decode_token = request.app.state.authenticate.decode_token(token)
    repo = repository.Device(request.app.state.database)
    return repo.get_devices(decode_token.get('sub'))


# @router.get('/device/{sensor_id}', status_code=status.HTTP_200_OK)
# async def read_users_me(request: Request, token: str = Depends(oauth2_scheme)):
#     decode_token = request.app.state.authenticate.decode_token(token)
#     repo = repository.Device(request.app.state.database)
#     return repo.get_devices(decode_token.get('sub'))
