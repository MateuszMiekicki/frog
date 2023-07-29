from fastapi import APIRouter, status, Request, HTTPException
from controller.dto.user import User, Email
import controller.facade.user_repository as facade_repository
import repository.user as repository
import controller.facade.user_authenticator as facade_authenticator
import security.hashing as hashing
import secrets
import string
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


def __generate_new_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(20))
    return password


@router.post('/login/forgot-password', status_code=status.HTTP_200_OK)
async def reset_password(request: Request, user: Email):
    database = request.app.state.postgresql
    user_repository = repository.User(database)
    user = user_repository.get_user(user.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found')
    new_password = __generate_new_password()
    mailer = request.app.state.mailer
    mailer.send_noreply_email(user.email,
                              'New password', new_password)
    new_password = hashing.hash(new_password)

    user_repository.change_password(user.id, new_password)
    return {'detail': f'new password send to {user.email}'}
