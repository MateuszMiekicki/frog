from fastapi import FastAPI
from configuration import logger, configuration
from controller import register, login, device, data, sensor, alert, user
from security.authenticate import Authenticate
from fastapi.security import HTTPBearer
import repository.user as repository
import sys
import zmq.asyncio
import asyncio
import logging

app = FastAPI()
app.include_router(register.router)
app.include_router(login.router)
app.include_router(device.router)
app.include_router(data.router)
app.include_router(sensor.router)
app.include_router(alert.router)
app.include_router(user.router)


@app.on_event('startup')
async def startup():
    app.state.postgresql = configuration.create_postgresql_instance()
    app.state.questdb = configuration.create_questdb_instance()
    app.state.mailer = configuration.create_mailer_instance()
    app.state.authenticate = Authenticate()
    app.state.security = HTTPBearer()

    host_for_requester = "toad"
    port_for_requester = 5571
    poller_timeout_for_requester = 5
    zmq_config = configuration.ConfigForRequest(
        zmq.asyncio.Context(), f"tcp://{host_for_requester}:{port_for_requester}", poller_timeout_for_requester)
    app.state.zmq_config = zmq_config
    logging.info(
        f"ZMQ requester initialized on port {port_for_requester} and host {host_for_requester} with timeout {poller_timeout_for_requester} seconds")

if __name__ == '__main__':
    configuration.set_event_loop_policy()
    configuration.parse_args()
    frog_config = configuration.FrogConfiguration(
        configuration.read_config_from_file(configuration.configuration_files['frog']))
    logger.set_log_level(frog_config.get_log_level())
    import uvicorn
    uvicorn.run(app, lifespan="on", host=frog_config.get_hostname(), port=frog_config.get_port(),
                log_level='debug', log_config=None)
    # ,ssl_keyfile='private/key.pem', ssl_certfile='private/cert.pem')
