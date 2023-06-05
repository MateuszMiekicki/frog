from fastapi import HTTPException, status


def is_device_exists(device, device_id):
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'The device with the id {device_id} was not found.')
    return True


def is_device_owned_by_user(device, user_id):
    if device.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'The device with the id {device.id} is not owned by you.')
    return True
