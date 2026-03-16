from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum
import uuid


class TransactionType(str, Enum):
    SUBSCRIPTION = "apertura"
    CANCELLATION = "cancelacion"


class TransactionStatus(str, Enum):
    PENDING = "pendiente"
    COMPLETED = "completada"
    FAILED = "fallida"


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


def generate_transaction_id() -> str:
    return f"TXN-{uuid.uuid4().hex[:12].upper()}"


class TransactionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    transaction_id: str = Field(default_factory=generate_transaction_id)
    user_id: str
    fund_id: int
    fund_name: str
    transaction_type: TransactionType
    amount: float = Field(..., ge=0)
    status: TransactionStatus = TransactionStatus.COMPLETED
    previous_balance: float = Field(..., ge=0)
    new_balance: float = Field(..., ge=0)
    notification_sent: bool = False
    notification_type: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class SubscriptionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    fund_id: int
    fund_name: str
    amount: float = Field(..., ge=0)
    subscription_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    cancellation_date: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
