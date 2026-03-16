from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator
from app.models.user import NotificationPreference, UserRole
import re


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{6,14}$')
    notification_preference: NotificationPreference = NotificationPreference.EMAIL


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('La password debe contener al menos una mayuscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La password debe contener al menos una minuscula')
        if not re.search(r'\d', v):
            raise ValueError('La password debe contener al menos un numero')
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{6,14}$')
    notification_preference: Optional[NotificationPreference] = None


class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    balance: float
    notification_preference: NotificationPreference
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True


class UserBalanceResponse(BaseModel):
    user_id: str
    email: str
    balance: float
    currency: str = "COP"


class UserSubscriptionsResponse(BaseModel):
    user_id: str
    email: str
    balance: float
    subscriptions: List["SubscriptionDetail"]
    total_invested: float


class SubscriptionDetail(BaseModel):
    subscription_id: str
    fund_id: int
    fund_name: str
    amount: float
    subscription_date: datetime
    category: str


UserSubscriptionsResponse.model_rebuild()
