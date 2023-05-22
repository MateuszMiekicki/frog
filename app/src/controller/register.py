from fastapi import APIRouter, status, Request, HTTPException
from controller.dto.user import User
import controller.facade.user_repository as facade
router = APIRouter()


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def login(request: Request, user: User):
    if facade.add_user(request.app.state.postgresql, user):
        return {'detail': 'user created'}
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f'User {user.email} exists')
