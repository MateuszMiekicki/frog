from repository import user as repo
import repository.user as repository
from fastapi import APIRouter, status, Request, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dto import user as dto
router = APIRouter()
security = HTTPBearer()

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: Request, user: dto.User):
    repo = repository.User(request.app.state.database)
    user_from_db = repo.get_user(user.email)
    if user_from_db:
        print("znalazło")
        print(user_from_db.password)
        print(user.password)
    if not user_from_db and user_from_db.password is not user.password:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    access_token = request.app.state.authenticate.encode_token(user_from_db)
    refresh_token = request.app.state.authenticate.encode_refresh_token(
        user_from_db)
    return {'access_token': access_token, 'refresh_token': refresh_token}
