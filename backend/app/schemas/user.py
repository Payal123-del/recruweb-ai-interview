from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from app.models.entities import UserRoleType


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: str = UserRoleType.RECRUITER.value
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    tenant_id: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserRead(UserBase):
    id: str
    tenant_id: Optional[str] = None
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(UserRead):
    permissions: List[str] = []
    company_name: Optional[str] = None
