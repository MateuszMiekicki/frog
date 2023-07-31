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
        timestamp, mac_address, pin_number, value = item
        timestamp_str = timestamp.isoformat()
        if str(mac_address) not in result:
            result[str(mac_address)] = {}
        if str(pin_number) not in result[str(mac_address)]:
            result[str(mac_address)][str(pin_number)] = {
                "timestamp": timestamp_str,
                "value": value
            }
        else:
            previous_timestamp_str = result[str(
                mac_address)][str(pin_number)]["timestamp"]
            previous_timestamp = datetime.fromisoformat(previous_timestamp_str)
            if timestamp > previous_timestamp:
                result[str(mac_address)][str(pin_number)] = {
                    "timestamp": timestamp_str,
                    "value": value
                }
                previous_values[(mac_address, pin_number)] = value
    return result


def prepare_query(devices):
    mac_addresses = ["'"+str(device.mac_address)+"'" for device in devices]
    data_for_specific_devices = "WHERE mac_address IN ({})".format(
        ','.join(mac_addresses))
    query = "SELECT * FROM sensor_data {} ORDER BY timestamp DESC".format(
        data_for_specific_devices)
    return query


class NoDeviceIdException(Exception):
    pass


async def get_data(database, devices):
    cursor = database.cursor()
    cursor.execute(prepare_query(devices))
    rows = cursor.fetchmany(size=50)
    logging.trace("Rows: {}".format(rows))
    return json.dumps(prepare_message_for_client(rows))


class Parameters():
    devices = None


def handle_message(message: str, parameters: Parameters):
    message = json.loads(message)
    if len(message["devices"]) == 0:
        parameters.devices = None
        return
    if message["devices"] is not None:
        parameters.devices = message["devices"]
        logging.debug("Devices: {}".format(parameters.devices))


async def authenticate_websocket(websocket: WebSocket):
    token = None
    try:
        message = await websocket.receive_text()
        message = json.loads(message)
        if message and 'token' in message:
            token = message["token"]
    except websockets.exceptions.ConnectionClosed:
        return None
    except Exception as e:
        logging.error(f"Error receive data: {str(e)}")
        return None
    authenticate = Authenticate()
    try:
        decoded_token = authenticate.decode_token(token)
    except HTTPException:
        await websocket.close(code=4401, reason="User not authorization")
        return None
    except Exception as e:
        logging.error(f"Error decode token: {str(e)}")
        await websocket.close(code=1008)
        return None
    return decoded_token.get("sub")


def intersection_sets_of_devices(set_with_device_id, set_with_device):
    verified_devices_id = list(
        set(set_with_device_id) & set([device.id for device in set_with_device]))
    verified_devices = []
    for device in set_with_device:
        if device.id in verified_devices_id:
            verified_devices.append(device)
    return verified_devices


def preprocessing_parameters_with_device_id(devices_from_client, devices_from_database):
    if devices_from_client is None and len(devices_from_database) != 0:
        return devices_from_database
    if len(devices_from_client) == 0:
        return None

    verified_devices = intersection_sets_of_devices(
        devices_from_client, devices_from_database)
    return verified_devices


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
        devices = preprocessing_parameters_with_device_id(
            parameters.devices, repo.get_devices_by_user_id(user_id))
        if devices is None or len(devices) == 0:
            await websocket.close(code=4406, reason="The user does not have a device")
            return
        try:
            data = await get_data(conn, devices)
            await websocket.send_text(data)
        except websockets.exceptions.ConnectionClosed:
            break
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            break
        end_time = time.time()
        elapsed_time = end_time - start_time
        delay = 1 - elapsed_time
        if delay > 0:
            await asyncio.sleep(delay)


@router.websocket("/device/{device_id}/sensor/data")
async def data_sensors(websocket: WebSocket, device_id: int):
    await websocket.accept()
    user_id = await authenticate_websocket(websocket)
    if user_id is None:
        logging.error("User not authorization")
        return
    conn = websocket.app.state.questdb
    repo = repository.Device(websocket.app.state.postgresql)
    devices = preprocessing_parameters_with_device_id(
        [device_id], repo.get_devices_by_user_id(user_id))
    if devices is None or len(devices) == 0:
        await websocket.close(code=4406, reason="The user does not have a device")
        logging.error("The user does not have a device")
        return
    while True:
        start_time = time.time()
        try:
            logging.debug("Get data")
            data = await get_data(conn, devices)
            logging.debug("Send data")
            await websocket.send_text(data)
            logging.debug("Data sent")
        except websockets.exceptions.ConnectionClosed:
            logging.error("Connection closed")
            break
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            break
        end_time = time.time()
        elapsed_time = end_time - start_time
        delay = 1 - elapsed_time
        logging.debug("Delay: {}".format(delay))
        if delay > 0:
            await asyncio.sleep(delay)
