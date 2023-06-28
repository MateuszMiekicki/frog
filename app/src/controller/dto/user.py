from pydantic import BaseModel, EmailStr, SecretStr


class User(BaseModel):
    email: EmailStr
    password: SecretStr


class SimplifyUser(BaseModel):
    email: EmailStr
