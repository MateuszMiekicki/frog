from fastapi import APIRouter, status, Request, HTTPException
from controller.dto.user import User, Email
import uuid
import repository.user as user_repo
import repository.user_confirmation as user_confirmation_repo
import security.hashing as hashing
import base64
import logging
router = APIRouter()


def __generate_code(user_email: str):
    def __generate_uuid():
        return str(uuid.uuid4())
    confirmation_code = __generate_uuid() + user_email
    confirmation_code = hashing.hash(confirmation_code)
    return base64.b64encode(confirmation_code.encode('utf-8')).decode('utf-8')


def __send_confirmation_code(mailer, user_email):
    confirmation_code = __generate_code(user_email)
    try:
        mailer.send_noreply_email(user_email,
                                  'Confirm registration', confirmation_code)
    except Exception as error:
        logging.error(error)
    return confirmation_code


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(request: Request, user: User):
    database = request.app.state.postgresql
    user_repository = user_repo.User(database)
    if not user_repository.is_user_exist(user.email):
        added_user = user_repository.add_user(email=user.email,
                                              password=hashing.hash(user.password.get_secret_value()))
        mailer = request.app.state.mailer
        confirmation_code = __send_confirmation_code(mailer, user.email)
        user_confirmation_repository = user_confirmation_repo.UserConfirmation(
            database)
        user_confirmation_repository.add_user_confirmation_code(
            added_user.id, confirmation_code)
        return {'detail': 'user created'}
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f'User {user.email} exists')


@router.post('/register/resend', status_code=status.HTTP_200_OK)
async def resend_confirmation_code(request: Request, user: Email):
    database = request.app.state.postgresql
    user_repository = user_repo.User(database)
    user = user_repository.get_user(user.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User {user.email} does not exist')
    if user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'User {user.email} is already confirmed')
    mailer = request.app.state.mailer
    confirmation_code = __send_confirmation_code(mailer, user.email)
    user_confirmation_repository = user_confirmation_repo.UserConfirmation(
        database)
    user_confirmation_repository.add_user_confirmation_code(
        user.id, confirmation_code)
    return {'detail': 'confirmation code sent'}


@router.get("/register/{confirmation_code}", status_code=status.HTTP_202_ACCEPTED)
def confirm_registration(request: Request, confirmation_code: str):
    database = request.app.state.postgresql
    user_confirmation_repository = user_confirmation_repo.UserConfirmation(
        database)
    code_wit_user_id = user_confirmation_repository.get_by_confirmation_code(
        confirmation_code)
    if not code_wit_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Confirmation code {confirmation_code} does not exist')
    user_repository = user_repo.User(database)
    user_repository.change_active_status(code_wit_user_id.user_id, True)
    user_confirmation_repository.delete_confirmation_code(confirmation_code)
    return {'detail': 'user confirmed'}
