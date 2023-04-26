from fastapi import APIRouter, status, Request, HTTPException, Depends, WebSocket
import asyncio
from fastapi import FastAPI
import psycopg as pg
import time
import psycopg2
import json
from datetime import datetime
from configuration import logger
router = APIRouter()


conn = psycopg2.connect(database="qdb",
                        host="localhost",
                        user="frogReadOnly",
                        password="frog!123",
                        port="8812")


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
        ', '.join(devices_id)) if devices_id is not None and len(devices_id) > 0 else ""
    query = "SELECT * FROM sensor_data {} ORDER BY timestamp DESC".format(
        data_for_specific_device_id)
    return query


async def get_data(devices_id=None):
    cursor = conn.cursor()
    cursor.execute(prepare_query(devices_id))
    rows = cursor.fetchmany(size=50)
    return json.dumps(prepare_message_for_client(rows))


class Parameters():
    devices = None


async def handle_message(message: str, parameters: Parameters):
    message = json.loads(message)
    if message["devices"] is not None:
        parameters.devices = message["devices"]
        logging.debug("Devices: {}".format(parameters.devices))


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    parameters = Parameters()

    async def listen_for_messages():
        while True:
            message = await websocket.receive_text()
            if message:
                await handle_message(message, parameters)

    asyncio.create_task(listen_for_messages())

    while True:
        start_time = time.time()

        data = await get_data(parameters.devices)
        await websocket.send_json(data)

        end_time = time.time()
        elapsed_time = end_time - start_time
        delay = 1 - elapsed_time
        if delay > 0:
            await asyncio.sleep(delay)
