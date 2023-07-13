from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import repository.alert as alertRepository
import repository.device as deviceRepository
import logging
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

router = APIRouter()


def __extract_device_id_from_request(request: Request):
    return [device.id for device in request]


@router.put('/devices/alerts/{alert_id}', status_code=status.HTTP_200_OK)
async def serve_alert(request: Request, alert_id: int, token: str = Depends(oauth2_scheme)):
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
    alert_repository.serve_alert(alert_id)
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


@router.get('/devices/alerts/', status_code=status.HTTP_200_OK)
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
