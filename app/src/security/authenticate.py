import jwt
import bcrypt
import entity.user as entity
from sqlalchemy.orm import Session
import os
from fastapi import HTTPException
from datetime import datetime, timedelta
import ecdsa


class Authenticate():
    SECRET_KEY = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p).to_pem()
    ALGORITHM = 'ES256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    def __init__(self):
        print(self.SECRET_KEY)

    def encode_token(self, user):
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow(),
            'scope': 'access_token',
            'sub': user.id,
            'role': user.role_id
        }
        return jwt.encode(
            payload,
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.SECRET_KEY,
                                 algorithms=[self.ALGORITHM])
            if (payload['scope'] == 'access_token'):
                return payload
            raise HTTPException(
                status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')
