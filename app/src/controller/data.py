from typing import Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from security import hashing
from fastapi import APIRouter, status, Request, HTTPException, Depends, WebSocket
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import repository.device as repository
from dto.device import Device
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
        except WebSocketDisconnect:
            break
