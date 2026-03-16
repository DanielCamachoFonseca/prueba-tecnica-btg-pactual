from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.fund import FundCategory


class FundBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    minimum_amount: float = Field(..., ge=0)
    category: FundCategory
    description: Optional[str] = None


class FundCreate(FundBase):
    fund_id: int = Field(..., ge=1)


class FundUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    minimum_amount: Optional[float] = Field(None, ge=0)
    category: Optional[FundCategory] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class FundResponse(BaseModel):
    id: str = Field(..., alias="_id")
    fund_id: int
    name: str
    minimum_amount: float
    category: FundCategory
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True


class FundListResponse(BaseModel):
    funds: List[FundResponse]
    total: int


class FundSummary(BaseModel):
    fund_id: int
    name: str
    minimum_amount: float
    category: str
    is_available: bool = True
