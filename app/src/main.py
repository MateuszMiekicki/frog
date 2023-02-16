from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from controller import register, login, device
from configure import database
from security.authenticate import Authenticate
from fastapi.security import HTTPBearer
import repository.user as repository


app = FastAPI()
app.include_router(register.router)
app.include_router(login.router)
app.include_router(device.router)


@app.on_event('startup')
async def startup():
    auth = database.DatabaseAuth('frog', 'frog!123')
    print("db:5400")
    address = database.DatabaseAddress('db', 5432)
    dialect = database.Dialect.postgresql
    driver = database.Driver.none
    database_name = 'frog'
    db = database.Database()
    db.connect(
        dialect, driver, address, database_name, auth)
    app.state.database = db
    app.state.authenticate = Authenticate()
    app.state.security = HTTPBearer()

    repo = repository.User(app.state.database)
    # if repo.is_user_exist('admin') is False:
    #     pwhash = bcrypt.hashpw('admin'.encode('utf8'), bcrypt.gensalt())
    #     password = pwhash.decode('utf8')
    #     user_entity = entity.User('admin', 'admin', password, 1)
    #     repo.insert(user_entity)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
    # ,ssl_keyfile='private/key.pem', ssl_certfile='private/cert.pem')
