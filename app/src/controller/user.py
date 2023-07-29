from fastapi import APIRouter, status, Request, HTTPException
from controller.dto.user import Password
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends
import repository.user as repository
import security.hashing as hashing
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.post("/account/user/change-password", status_code=status.HTTP_200_OK)
async def change_password(request: Request, password: Password, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    user_id = decoded_token.get('sub')
    user_repository = repository.User(request.app.state.postgresql)
    user_repository.change_password(
        user_id, hashing.hash(password.password.get_secret_value()))
    return {"message": "Password changed"}
