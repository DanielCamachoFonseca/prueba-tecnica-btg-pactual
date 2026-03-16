from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from enum import Enum


class NotificationPreference(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    BOTH = "both"
    NONE = "none"


class UserRole(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    hashed_password: str
    full_name: str
    phone: Optional[str] = None
    balance: float = Field(default=500000.0, ge=0)
    notification_preference: NotificationPreference = NotificationPreference.EMAIL
    role: UserRole = UserRole.CLIENT
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class UserInDB(UserModel):
    subscriptions: List[str] = Field(default_factory=list)
