from fastapi import FastAPI
from configuration import logger, database, configuration
from controller import register, login, device, data
from security.authenticate import Authenticate
from fastapi.security import HTTPBearer
import repository.user as repository


app = FastAPI()
app.include_router(register.router)
app.include_router(login.router)
app.include_router(device.router)
app.include_router(data.router)


@app.on_event('startup')
async def startup():
    postgresql_config = configuration.PostgreSQLConfiguration(
        configuration.read_config_from_file('configuration/private/template/databases.properties'))
    auth = database.DatabaseAuth(
        postgresql_config.get_user_name(), postgresql_config.get_password())
    address = database.DatabaseAddress(
        postgresql_config.get_hostname(), postgresql_config.get_port())
    dialect = database.Dialect.postgresql
    driver = database.Driver.none
    db = database.Database()
    db.connect(dialect, driver, address,
               postgresql_config.get_database_name(), auth)
    app.state.database = db
    app.state.authenticate = Authenticate()
    app.state.security = HTTPBearer()

    repo = repository.User(app.state.database)


if __name__ == '__main__':
    frog_config = configuration.FrogConfiguration(
        configuration.read_config_from_file('configuration/private/template/frog.properties'))
    logger.set_log_level(frog_config.get_log_level())
    import uvicorn
    uvicorn.run(app, host=frog_config.get_hostname(), port=frog_config.get_port(),
                log_level='info', log_config=None)
    # ,ssl_keyfile='private/key.pem', ssl_certfile='private/cert.pem')
