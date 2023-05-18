from repository import user as repo
import repository.user as repository
from fastapi import APIRouter, status, Request, HTTPException
from dto.user import User
from security import hashing
router = APIRouter()


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def login(request: Request, user: User):
    repo = repository.User(request.app.state.postgresql)
    user.email = user.email.lower()
    if repo.is_user_exist(user.email.lower()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'User {user.email} exists')
    repo.add_user(email=user.email,
                  password=hashing.hash(user.password.get_secret_value()), role='owner')
    return {'detail': 'user created'}
