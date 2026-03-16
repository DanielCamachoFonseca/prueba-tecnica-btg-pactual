from typing import Any, Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    success: bool = False


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthResponse(BaseModel):
    status: str
    database: str
    version: str
    timestamp: str
