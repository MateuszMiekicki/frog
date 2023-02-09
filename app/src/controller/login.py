from fastapi import APIRouter, status, Request, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dto import user as dto
router = APIRouter()
security = HTTPBearer()


from repository import user as repo

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: Request, user: dto.Login):
    user_from_db = request.app.state.authenticate.authenticate(
        user.login, user.password)
    if user_from_db is None:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    access_token = request.app.state.authenticate.encode_token(user_from_db)
    refresh_token = request.app.state.authenticate.encode_refresh_token(
        user_from_db)
    return {'access_token': access_token, 'refresh_token': refresh_token}