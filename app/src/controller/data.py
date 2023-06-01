import traceback
from fastapi import APIRouter, status, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
import websockets
import asyncio
from fastapi import FastAPI
import time
import psycopg2
import json
from datetime import datetime
import logging
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from security.authenticate import Authenticate
from fastapi import APIRouter, status, Request, HTTPException, Depends
import repository.device as repository
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def prepare_message_for_client(rows):
    result = {}
    previous_values = {}
    for item in rows:
        timestamp, sensor_id, value1, value2 = item
        timestamp_str = timestamp.isoformat()
        if str(sensor_id) not in result:
            result[str(sensor_id)] = {}
        if str(value1) not in result[str(sensor_id)]:
            result[str(sensor_id)][str(value1)] = {
                "timestamp": timestamp_str,
                "value": value2
            }
        else:
            previous_timestamp_str = result[str(
                sensor_id)][str(value1)]["timestamp"]
            previous_timestamp = datetime.fromisoformat(previous_timestamp_str)
            if timestamp > previous_timestamp:
                result[str(sensor_id)][str(value1)] = {
                    "timestamp": timestamp_str,
                    "value": value2
                }
                previous_values[(sensor_id, value1)] = value2
    return result


def prepare_query(devices_id=None):
    data_for_specific_device_id = "WHERE device_id IN ({})".format(
        ','.join(map(str, devices_id))) if devices_id is not None and len(devices_id) > 0 else ""
    query = "SELECT * FROM sensor_data {} ORDER BY timestamp DESC".format(
        data_for_specific_device_id)
    return query


class NoDeviceIdException(Exception):
    pass


async def get_data(database, devices_id):
    if devices_id is None or len(devices_id) == 0:
        raise NoDeviceIdException("No devices id")
    cursor = database.cursor()
    cursor.execute(prepare_query(devices_id))
    rows = cursor.fetchmany(size=50)
    return json.dumps(prepare_message_for_client(rows))


class Parameters():
    verified = False
    devices = None


def handle_message(message: str, parameters: Parameters):
    message = json.loads(message)
    if len(message["devices"]) == 0:
        parameters.devices = None
        return
    if message["devices"] is not None:
        parameters.verified = False
        parameters.devices = message["devices"]
        logging.debug("Devices: {}".format(parameters.devices))


async def authenticate_websocket(websocket: WebSocket):
    token = None
    if "token" in websocket.headers:
        token = websocket.headers["token"]
    authenticate = Authenticate()
    try:
        decoded_token = authenticate.decode_token(token)
    except HTTPException:
        await websocket.close(code=4001, reason="User not authorization")
        return None
    except Exception as e:
        logging.error(f"Error decode token: {str(e)}")
        await websocket.close(code=1008)
        return None
    return decoded_token.get("sub")


def get_devices_id_from_devices_list(devices):
    devices_id = []
    for device in devices:
        devices_id.append(device.id)
    return devices_id


def verify_devices_id(parameters, devices_from_database):
    devices_id_from_database = get_devices_id_from_devices_list(
        devices_from_database)
    parameters.verified = True
    return list(set(parameters.devices) & set(devices_id_from_database))


@router.websocket("/device/sensor/data")
async def data_sensors(websocket: WebSocket):
    await websocket.accept()
    user_id = await authenticate_websocket(websocket)
    if user_id is None:
        return
    conn = websocket.app.state.questdb
    parameters = Parameters()

    async def listen_for_messages():
        while True:
            try:
                message = await websocket.receive_text()
                if message:
                    handle_message(message, parameters)
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                logging.error(f"Error receive data: {str(e)}")
                break

    asyncio.create_task(listen_for_messages())
    repo = repository.Device(websocket.app.state.postgresql)
    while True:
        start_time = time.time()
        if parameters.devices is None:
            parameters.devices = repo.get_devices(user_id)
            parameters.devices = get_devices_id_from_devices_list(
                parameters.devices)
            logging.debug("User devices with id {}: {}".format(
                user_id, parameters.devices))
        elif not parameters.verified:
            parameters.devices = verify_devices_id(
                parameters, repo.get_devices(user_id))
            logging.debug("User devices with id {}: {}".format(
                user_id, parameters.devices))
        try:
            data = await get_data(conn, parameters.devices)
            await websocket.send_text(data)
        except websockets.exceptions.ConnectionClosed:
            break
        except NoDeviceIdException:
            await websocket.close(code=4004, reason=f"user {user_id} has no devices")
            break
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            break
        end_time = time.time()
        elapsed_time = end_time - start_time
        delay = 1 - elapsed_time
        if delay > 0:
            await asyncio.sleep(delay)
