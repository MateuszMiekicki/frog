from fastapi import APIRouter, status, Request, HTTPException
from controller.dto.user import User
import controller.facade.user_repository as facade_repository
import controller.facade.user_authenticator as facade_authenticator
router = APIRouter()


@router.post('/account/user', status_code=status.)
async def change_password(request: Request, user: User):
    if not facade_authenticator.is_authenticated(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    facade_repository.change_password(user)
    return {"message": "Password changed"}
