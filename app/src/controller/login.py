import repository.user as repository
from fastapi import APIRouter, status, Request, HTTPException
from dto.user import User
from security import hashing
router = APIRouter()


@router.post('/login', status_code=status.HTTP_200_OK)
async def login(request: Request, user: User):
    repo = repository.User(request.app.state.database)
    user.email = user.email.lower()
    user_from_db = repo.get_user(user.email)
    if user_from_db and hashing.verify(user_from_db.password, user.password.get_secret_value()):
        access_token = request.app.state.authenticate.encode_token(
            user_from_db)
        return {'access_token': access_token, 'token_type': 'bearer'}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password')
