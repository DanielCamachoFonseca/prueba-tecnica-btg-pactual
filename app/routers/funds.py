from fastapi import APIRouter, Depends, Query, status
from typing import List

from app.schemas.fund import FundResponse, FundListResponse, FundCreate, FundUpdate
from app.services.fund_service import FundService
from app.core.security import get_current_user_id, require_admin

router = APIRouter(prefix="/funds", tags=["Fondos de Inversion"])


@router.get(
    "",
    response_model=FundListResponse,
    summary="Listar fondos disponibles"
)
async def get_all_funds(
    include_inactive: bool = Query(False),
    _: str = Depends(get_current_user_id)
):
    funds = await FundService.get_all_funds(include_inactive=include_inactive)
    return FundListResponse(funds=funds, total=len(funds))


@router.get(
    "/{fund_id}",
    response_model=FundResponse,
    summary="Obtener fondo por ID"
)
async def get_fund(
    fund_id: int,
    _: str = Depends(get_current_user_id)
):
    fund = await FundService.get_fund_by_id(fund_id)
    return fund


@router.post(
    "",
    response_model=FundResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo fondo (Admin)",
    dependencies=[Depends(require_admin)]
)
async def create_fund(fund_data: FundCreate):
    fund = await FundService.create_fund(fund_data)
    return fund


@router.put(
    "/{fund_id}",
    response_model=FundResponse,
    summary="Actualizar fondo (Admin)",
    dependencies=[Depends(require_admin)]
)
async def update_fund(fund_id: int, fund_update: FundUpdate):
    fund = await FundService.update_fund(fund_id, fund_update)
    return fund
