from fastapi import APIRouter, status, Request, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dto import user as dto
router = APIRouter()
security = HTTPBearer()


from repository import user as repo

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def login(request: Request, user: dto.User):
    if repo.is_user_exist(user.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f'User {user.email} exists')
    repo.add_user(user.email, user.password, 'user')

    return {"sdf": "asd"}
