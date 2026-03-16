from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest
)
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user_id
)
from app.core.config import settings
from app.core.exceptions import InvalidCredentialsException

router = APIRouter(prefix="/auth", tags=["Autenticacion"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario"
)
async def register(user_data: UserCreate):
    user = await UserService.create_user(user_data)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesion"
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserService.authenticate_user(
        email=form_data.username,
        password=form_data.password
    )
    
    # Crear tokens
    token_data = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"]
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar token de acceso"
)
async def refresh_token(request: RefreshTokenRequest):
    payload = decode_token(request.refresh_token)
    
    # Verificar que es un refresh token
    if payload.get("type") != "refresh":
        raise InvalidCredentialsException()
    
    # Crear nuevo access token
    token_data = {
        "sub": payload["sub"],
        "email": payload.get("email"),
        "role": payload.get("role", "client")
    }
    
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario actual",
    description="Retorna información del usuario autenticado"
)
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """
    Obtiene los datos del usuario actualmente autenticado.
    """
    user = await UserService.get_user_by_id(user_id)
    return user
