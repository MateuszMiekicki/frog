from security import hashing
from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import repository.device as repository
from dto.device import Device


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/device", status_code=status.HTTP_200_OK)
async def read_users_me(request: Request, device: Device, token: str = Depends(oauth2_scheme)):
    decode_token = request.app.state.authenticate.decode_token(token)
    repo = repository.Device(request.app.state.database)
    repo.add_device(decode_token.get("sub"), device.name, device.key)
    return "asd"
