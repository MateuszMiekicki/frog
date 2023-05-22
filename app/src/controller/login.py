from fastapi import APIRouter, status, Request, HTTPException
from controller.dto.user import User
import controller.facade.user_repository as facade_repository
import controller.facade.user_authenticator as facade_authenticator
router = APIRouter()


@router.post('/login', status_code=status.HTTP_200_OK)
async def login(request: Request, user: User):
    user_from_db = facade_repository.verify_user(
        request.app.state.postgresql, user)
    if user_from_db:
        return facade_authenticator.authenticate(
            user_from_db, request.app.state.authenticate)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password')
