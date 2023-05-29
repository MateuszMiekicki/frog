from fastapi import APIRouter, status, Request, HTTPException
from controller.dto.user import User
import controller.facade.user_repository as facade_repository
import controller.facade.user_authenticator as facade_authenticator
import zmq
import time
router = APIRouter()

zmq_server_address = 'tcp://localhost:5555'


@router.get('/device/{device_id}/configuration', status_code=status.HTTP_200_OK)
async def get_config(request: Request):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(zmq_server_address)
    socket.send_string("Hello, server!")
    response = ''
    if socket.poll(timeout=1000):
        response = socket.recv_string()
        print("Response:", response)
    else:
        print("Przekroczono limit czasu oczekiwania")
    socket.close()
    context.term()
    return response
