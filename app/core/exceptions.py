from fastapi import HTTPException, status
from typing import Optional, Dict


class BTGException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class InsufficientBalanceException(BTGException):
    def __init__(self, fund_name: str, required_amount: float, available_balance: float):
        detail = f"No tiene saldo disponible para vincularse al fondo {fund_name}"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INSUFFICIENT_BALANCE"
        )
        self.fund_name = fund_name
        self.required_amount = required_amount
        self.available_balance = available_balance


class FundNotFoundException(BTGException):
    def __init__(self, fund_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fondo con ID {fund_id} no encontrado",
            error_code="FUND_NOT_FOUND"
        )


class SubscriptionNotFoundException(BTGException):
    def __init__(self, subscription_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suscripcion con ID {subscription_id} no encontrada",
            error_code="SUBSCRIPTION_NOT_FOUND"
        )


class AlreadySubscribedException(BTGException):
    def __init__(self, fund_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya esta suscrito al fondo {fund_name}",
            error_code="ALREADY_SUBSCRIBED"
        )


class UserNotFoundException(BTGException):
    def __init__(self, user_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado",
            error_code="USER_NOT_FOUND"
        )


class UserAlreadyExistsException(BTGException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario con el email {email}",
            error_code="USER_ALREADY_EXISTS"
        )


class InvalidCredentialsException(BTGException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password incorrectos",
            error_code="INVALID_CREDENTIALS",
            headers={"WWW-Authenticate": "Bearer"}
        )


class SubscriptionNotActiveException(BTGException):
    def __init__(self, subscription_id: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La suscripcion {subscription_id} no esta activa",
            error_code="SUBSCRIPTION_NOT_ACTIVE"
        )
