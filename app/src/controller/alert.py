from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import repository.alert as alertRepository
import repository.device as deviceRepository
import logging
from controller.data import authenticate_websocket
from fastapi import WebSocket
import zmq
from sse_starlette.sse import EventSourceResponse
import requester.requester as sender

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

router = APIRouter()


def __extract_device_id_from_request(request: Request):
    return [device.id for device in request]


def __extract_device_with_concrete_id(id: int, devices):
    for device in devices:
        if device.id == id:
            return device
    return None


@router.put('/devices/alerts/{alert_id}', status_code=status.HTTP_200_OK)
async def serve_alert(request: Request, alert_id: int, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    user_id = decoded_token.get('sub')

    alert_repository = alertRepository.Alert(request.app.state.postgresql)
    alert = alert_repository.get_alert_by_id(alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The alert with the id {alert_id} was not found.')

    devices = deviceRepository.Device(
        request.app.state.postgresql).get_devices_by_user_id(user_id)
    device_id = alert.device_id if alert.device_id in __extract_device_id_from_request(
        devices) else None
    if device_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'The alert with the id {alert_id} is not owned by you.')

    alert_repository.serve_alert(alert_id)

    requester = sender.Requester(request.app.state.zmq_config)
    device_requester = sender.DeviceRequester(requester)

    device = __extract_device_with_concrete_id(device_id, devices)
    await device_requester.send_alert_served_indication_to_device(
        device.mac_address, alert_id)

    return {'detail': f'alert with id {alert_id} served'}


@router.delete('/devices/alerts/{alert_id}', status_code=status.HTTP_200_OK)
async def delete_alert(request: Request, alert_id: int, token: str = Depends(oauth2_scheme)):
    decoded_token = request.app.state.authenticate.decode_token(token)
    database = request.app.state.postgresql
    device_repository = deviceRepository.Device(database)
    user_id = decoded_token.get('sub')
    devices = device_repository.get_devices_by_user_id(user_id)
    alert_repository = alertRepository.Alert(database)
    devices_id = __extract_device_id_from_request(devices)
    if len(devices_id) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The user with the id {user_id} has no devices.')
    alert = alert_repository.get_alert_by_id(alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The alert with the id {alert_id} was not found.')
    if alert.device_id != devices_id[0]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'The alert with the id {alert_id} is not owned by you.')
    alert_repository.delete_alert(alert_id)
    return {'detail': f'alert with id {alert_id} deleted'}


@router.get('/devices/alerts', status_code=status.HTTP_200_OK)
async def get_alerts_with_parameters(request: Request,
                                     skip: int = 0,
                                     limit: int = 10,
                                     sort_by_priority: bool = False,
                                     sort_by_date: bool = False,
                                     only_served: bool = False,
                                     only_not_served: bool = False,
                                     token: str = Depends(oauth2_scheme)):
    logging.debug(
        f"get_alerts_with_parameters  skip: {skip}, limit: {limit}, sort_by_priority: {sort_by_priority}, sort_by_date: {sort_by_date}, only_served: {only_served}, only_not_served: {only_not_served}")
    decoded_token = request.app.state.authenticate.decode_token(token)
    database = request.app.state.postgresql
    device_repository = deviceRepository.Device(database)
    user_id = decoded_token.get('sub')
    devices = device_repository.get_devices_by_user_id(user_id)
    alert_repository = alertRepository.Alert(database)
    devices_id = __extract_device_id_from_request(devices)
    if len(devices_id) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The user with the id {user_id} has no devices.')
    return alert_repository.get_alerts_with_parameters(
        device_id=devices_id[0],
        skip=skip,
        limit=limit,
        sort_by_priority=sort_by_priority,
        sort_by_date=sort_by_date,
        only_served=only_served,
        only_not_served=only_not_served)


@router.websocket("/devices/notifier/alerts")
async def device_alerts_notifier(websocket: WebSocket):
    await websocket.accept()
    user_id = await authenticate_websocket(websocket)
    if user_id is None:
        return

    devices = deviceRepository.Device(
        websocket.app.state.postgresql).get_devices_by_user_id(user_id)
    if len(devices) == 0:
        await websocket.close(code=4404, reason="The user does not have a device")
        return
    sock = websocket.app.state.zmq_config.get_context().socket(zmq.SUB)
    sock.connect("tcp://localhost:5574")
    for device in devices:
        print(f"subscribing to {device.mac_address}")
        sock.setsockopt(zmq.SUBSCRIBE, str(device.mac_address).encode())

    try:
        while True:
            msg = await sock.recv_string()
            await websocket.send_text(msg)
    finally:
        sock.setsockopt(zmq.LINGER, 0)
        sock.close()


@router.get('/devices/notifier/alerts')
async def message_stream(request: Request, token: str = Depends(oauth2_scheme)):
    decode_token = request.app.state.authenticate.decode_token(token)

    devices = deviceRepository.Device(
        request.app.state.postgresql).get_devices_by_user_id(decode_token.get('sub'))
    if len(devices) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The user with the id {decode_token.get("sub")} has no devices.')

    client = request.app.state.zmq_config.zmq_context.socket(zmq.SUB)
    client.connect("tcp://localhost:5574")
    for device in devices:
        print(f"subscribing to {device.mac_address}")
        client.setsockopt(zmq.SUBSCRIBE, str(device.mac_address).encode())

    async def event_generator():
        while True:
            if await request.is_disconnected():
                client.close()
                break
            alert = await client.recv_string()
            yield alert

    return EventSourceResponse(event_generator())
