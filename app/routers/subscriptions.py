from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from app.schemas.transaction import (
    SubscriptionRequest,
    CancellationRequest,
    SubscriptionResponse,
    CancellationResponse,
    TransactionHistoryResponse,
    UserActiveSubscriptionsResponse
)
from app.services.transaction_service import TransactionService
from app.core.security import get_current_user_id
from app.models.transaction import TransactionType

router = APIRouter(prefix="/subscriptions", tags=["Suscripciones"])


@router.post(
    "",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Suscribirse a un fondo"
)
async def subscribe_to_fund(
    request: SubscriptionRequest,
    user_id: str = Depends(get_current_user_id)
):
    result = await TransactionService.subscribe_to_fund(
        user_id=user_id,
        fund_id=request.fund_id
    )
    return result


@router.delete(
    "/{subscription_id}",
    response_model=CancellationResponse,
    summary="Cancelar suscripcion"
)
async def cancel_subscription(
    subscription_id: str,
    user_id: str = Depends(get_current_user_id)
):
    result = await TransactionService.cancel_subscription(
        user_id=user_id,
        subscription_id=subscription_id
    )
    return result


@router.get(
    "",
    response_model=UserActiveSubscriptionsResponse,
    summary="Ver suscripciones activas"
)
async def get_active_subscriptions(
    user_id: str = Depends(get_current_user_id)
):
    result = await TransactionService.get_user_active_subscriptions(user_id)
    return result


@router.get(
    "/history",
    response_model=TransactionHistoryResponse,
    summary="Ver historial de transacciones"
)
async def get_transaction_history(
    transaction_type: Optional[TransactionType] = Query(None),
    fund_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: str = Depends(get_current_user_id)
):
    result = await TransactionService.get_transaction_history(
        user_id=user_id,
        transaction_type=transaction_type,
        fund_id=fund_id,
        page=page,
        page_size=page_size
    )
    return result
