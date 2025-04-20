from pydantic import BaseModel
from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str | None = None
    exp: datetime | None = None
    type: str | None = None  # "access" o "refresh"

class TokenBlacklist(BaseModel):
    token: str
    expires_at: datetime

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    access_token: str
    refresh_token: str 