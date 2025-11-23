from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreateSchema(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100, pattern="^[a-zA-Z0-9_]+$")
    full_name: Optional[str] = Field(None, max_length=255)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip()


class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100, pattern="^[a-zA-Z0-9_]+$")
    full_name: Optional[str] = Field(None, max_length=255)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip() if v else None


class UserResponseSchema(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

