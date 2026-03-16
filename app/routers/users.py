from fastapi import APIRouter, Depends

from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserBalanceResponse
)
from app.services.user_service import UserService
from app.core.security import get_current_user_id

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener perfil"
)
async def get_profile(user_id: str = Depends(get_current_user_id)):
    user = await UserService.get_user_by_id(user_id)
    return user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Actualizar perfil"
)
async def update_profile(
    user_update: UserUpdate,
    user_id: str = Depends(get_current_user_id)
):
    user = await UserService.update_user(user_id, user_update)
    return user


@router.get(
    "/me/balance",
    response_model=UserBalanceResponse,
    summary="Consultar saldo"
)
async def get_balance(user_id: str = Depends(get_current_user_id)):
    user = await UserService.get_user_by_id(user_id)
    return UserBalanceResponse(
        user_id=user_id,
        email=user["email"],
        balance=user["balance"],
        currency="COP"
    )
