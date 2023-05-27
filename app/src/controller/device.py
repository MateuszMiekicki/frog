# from security import hashing
from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import repository.device as repository
from controller.dto.device import Device
# from messages import MCUConfigReq_pb2
# import zmq

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def __trim_key(key):
    return key.replace(' ', '')


def __cast_to_lower_case(key):
    return key.lower()


def prepare_key_to_add_to_database(key):
    return __cast_to_lower_case(__trim_key(key))


@router.post('/device', status_code=status.HTTP_201_CREATED)
async def read_users_me(request: Request, device: Device, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    repo = repository.Device(request.app.state.postgresql)
    if repo.get_device_by_key(device.key):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'The device with the key {device.key} is already in the database.')
    repo.add_device(decoded_token.get('sub'), device.name,
                    prepare_key_to_add_to_database(device.key))
    return {'detail': f'device with key {device.key} added'}


@router.get('/devices', status_code=status.HTTP_200_OK)
async def read_users_me(request: Request, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    repo = repository.Device(request.app.state.postgresql)
    return repo.get_devices(decoded_token.get('sub'))


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


# @router.get('/device/configuration/{device_id}', status_code=status.HTTP_201_CREATED)
# async def read_users_me(request: Request, device_id: int, token: str = Depends(oauth2_scheme)):
#     decode_token = request.app.state.authenticate.decode_token(token)
#     repo = repository.Device(request.app.state.postgresql)

#     device = repo.get_device_by_id(device_id)
#     if device is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'The device with the id {device_id} was not found.')
#     request = MCUConfigReq_pb2.MCUConfigReq()
#     request.key = device.key
#     request = request.SerializeToString()
#     context = zmq.Context()
#     socket = context.socket(zmq.DEALER)
#     socket.connect("tcp://localhost:5555")
#     socket.send(request)
#     response = socket.recv()
#     socket.close()
#     return response


# @router.get('/device/{sensor_id}', status_code=status.HTTP_200_OK)
# async def read_users_me(request: Request, token: str = Depends(oauth2_scheme)):
#     decode_token = request.app.state.authenticate.decode_token(token)
#     repo = repository.Device(request.app.state.postgresql )
#     return repo.get_devices(decode_token.get('sub'))
