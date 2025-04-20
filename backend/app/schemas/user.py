from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class UserBase(BaseModel):
    email: EmailStr
    username: str | None = None

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=20)

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not all([
            re.search(r'[A-Z]', v),
            re.search(r'[a-z]', v),
            re.search(r'[0-9]', v),
            re.search(r'[!@#$%^&*(),.?":{}|<>]', v)
        ]):
            raise ValueError('Password must contain uppercase, lowercase, number and special character')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True 