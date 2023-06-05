from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import repository.device as repository
from controller.dto.device import Device


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def __trim_mac_address(mac_address):
    return mac_address.replace(' ', '')


def __cast_to_lower_case(mac_address):
    return mac_address.lower()


def prepare_mac_address_to_add_to_database(mac_address):
    return __cast_to_lower_case(__trim_mac_address(mac_address))


@router.post('/device', status_code=status.HTTP_201_CREATED)
async def add_device(request: Request, device: Device, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    repo = repository.Device(request.app.state.postgresql)
    if repo.get_device_by_mac_address(device.mac_address):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'The device with the mac_address {device.mac_address} is already in the database.')
    repo.add_device(decoded_token.get('sub'), device.name,
                    prepare_mac_address_to_add_to_database(device.mac_address))
    return {'detail': f'device with mac address: {device.mac_address} added'}


@router.get('/devices', status_code=status.HTTP_200_OK)
async def get_devices(request: Request, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    repo = repository.Device(request.app.state.postgresql)
    return repo.get_devices_by_user_id(decoded_token.get('sub'))


@router.delete('/device/{device_id}', status_code=status.HTTP_200_OK)
def delete_device(request: Request, device_id: int, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    repo = repository.Device(request.app.state.postgresql)
    device = repo.get_device_by_id(device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The device with the id {device_id} was not found.')
    if device.user_id != decoded_token.get('sub'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'The device with the id {device_id} is not owned by you.')
    repo.delete_device(device_id)
    return {'detail': f'device with id {device_id} deleted'}
