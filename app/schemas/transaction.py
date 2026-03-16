from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.transaction import TransactionType, TransactionStatus


class SubscriptionRequest(BaseModel):
    fund_id: int = Field(..., ge=1)


class CancellationRequest(BaseModel):
    subscription_id: str


class SubscriptionResponse(BaseModel):
    subscription_id: str
    transaction_id: str
    user_id: str
    fund_id: int
    fund_name: str
    amount: float
    previous_balance: float
    new_balance: float
    notification_sent: bool
    notification_type: Optional[str]
    message: str
    created_at: datetime


class CancellationResponse(BaseModel):
    subscription_id: str
    transaction_id: str
    user_id: str
    fund_id: int
    fund_name: str
    amount_returned: float
    previous_balance: float
    new_balance: float
    notification_sent: bool
    message: str
    cancelled_at: datetime


class TransactionResponse(BaseModel):
    id: str = Field(..., alias="_id")
    transaction_id: str
    user_id: str
    fund_id: int
    fund_name: str
    transaction_type: TransactionType
    amount: float
    status: TransactionStatus
    previous_balance: float
    new_balance: float
    notification_sent: bool
    notification_type: Optional[str]
    created_at: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True


class TransactionHistoryResponse(BaseModel):
    user_id: str
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TransactionFilter(BaseModel):
    transaction_type: Optional[TransactionType] = None
    fund_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[TransactionStatus] = None


class ActiveSubscriptionResponse(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    fund_id: int
    fund_name: str
    amount: float
    subscription_date: datetime
    is_active: bool
    
    class Config:
        populate_by_name = True
        from_attributes = True


class UserActiveSubscriptionsResponse(BaseModel):
    user_id: str
    subscriptions: List[ActiveSubscriptionResponse]
    total_invested: float
    available_balance: float
