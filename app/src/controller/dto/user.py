from pydantic import BaseModel, EmailStr, SecretStr


class User(BaseModel):
    email: EmailStr
    password: SecretStr


class Email(BaseModel):
    email: EmailStr


class Password(BaseModel):
    password: SecretStr
