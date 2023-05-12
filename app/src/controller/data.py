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
router = APIRouter()


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
        ''.join(map(str, devices_id))) if devices_id is not None and len(devices_id) > 0 else ""
    query = "SELECT * FROM sensor_data {} ORDER BY timestamp DESC".format(
        data_for_specific_device_id)
    return query


async def get_data(database, devices_id=None):
    cursor = database.cursor()
    cursor.execute(prepare_query(devices_id))
    rows = cursor.fetchmany(size=50)
    return json.dumps(prepare_message_for_client(rows))


class Parameters():
    devices = None


def handle_message(message: str, parameters: Parameters):
    message = json.loads(message)
    if message["devices"] is not None:
        parameters.devices = message["devices"]
        logging.debug("Devices: {}".format(parameters.devices))


@router.websocket("/data")
async def data_sensors(websocket: WebSocket):
    await websocket.accept()
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
    while True:
        start_time = time.time()
        data = await get_data(conn, parameters.devices)
        try:
            await websocket.send_text(data)
        except websockets.exceptions.ConnectionClosed:
            break
        except Exception as e:
            logging.error(f"Error sending data: {str(e)}")
            break
        end_time = time.time()
        elapsed_time = end_time - start_time
        delay = 1 - elapsed_time
        if delay > 0:
            await asyncio.sleep(delay)
