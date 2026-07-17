from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import uuid

from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshToken(BaseModel):
    refresh_token: str
    model_config = ConfigDict(
        str_strip_whitespace=True
    )

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str

class UserCreate(UserBase):
    password: str

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    password: str | None = None

    model_config = ConfigDict(
        str_strip_whitespace=True
    )
