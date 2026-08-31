from typing import Optional, List
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CandidateAccessRequest(BaseModel):
    secure_token: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserTokenPayload(BaseModel):
    sub: str
    tenant_id: Optional[str] = None
    role: Optional[str] = None
    permissions: List[str] = []
    exp: Optional[int] = None
