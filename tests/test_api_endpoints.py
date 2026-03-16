"""
Pruebas de integración para los endpoints de la API.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bson import ObjectId
from datetime import datetime, timezone

from app.core.security import create_access_token


class TestAuthEndpoints:
    """Pruebas para endpoints de autenticación."""
    
    @pytest.mark.asyncio
    async def test_register_success(self, async_client):
        """Test registro exitoso de usuario."""
        user_data = {
            "email": "nuevo@btgpactual.com",
            "password": "Password123",
            "full_name": "Nuevo Usuario",
            "notification_preference": "email"
        }
        
        mock_user = {
            "_id": str(ObjectId()),
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "balance": 500000.0,
            "notification_preference": "email",
            "role": "client",
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        }
        
        with patch('app.routers.auth.UserService.create_user', AsyncMock(return_value=mock_user)):
            response = await async_client.post("/api/v1/auth/register", json=user_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == user_data["email"]
            assert data["balance"] == 500000.0
    
    @pytest.mark.asyncio
    async def test_register_password_validation(self, async_client):
        """Test validación de contraseña débil."""
        user_data = {
            "email": "nuevo@btgpactual.com",
            "password": "weak",  # Contraseña muy corta
            "full_name": "Nuevo Usuario"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_login_success(self, async_client, test_user_data):
        """Test login exitoso."""
        # OAuth2PasswordRequestForm espera form data, no JSON
        login_data = {
            "username": test_user_data["email"],
            "password": "Password123"
        }
        
        with patch('app.routers.auth.UserService.authenticate_user', AsyncMock(return_value=test_user_data)):
            response = await async_client.post("/api/v1/auth/login", data=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"


class TestFundsEndpoints:
    """Pruebas para endpoints de fondos."""
    
    @pytest.mark.asyncio
    async def test_get_funds_unauthorized(self, async_client):
        """Test acceso sin autorización."""
        response = await async_client.get("/api/v1/funds")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_funds_success(self, async_client, auth_headers):
        """Test obtener fondos con autorización."""
        mock_funds = [
            {
                "_id": str(ObjectId()),
                "fund_id": 1,
                "name": "FPV_BTG_PACTUAL_RECAUDADORA",
                "minimum_amount": 75000.0,
                "category": "FPV",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        with patch('app.routers.funds.FundService.get_all_funds', AsyncMock(return_value=mock_funds)):
            response = await async_client.get("/api/v1/funds", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "funds" in data
            assert data["total"] == 1


class TestSubscriptionsEndpoints:
    """Pruebas para endpoints de suscripciones."""
    
    @pytest.mark.asyncio
    async def test_subscribe_success(self, async_client, auth_headers):
        """Test suscripción exitosa a fondo."""
        subscription_data = {"fund_id": 1}
        
        mock_result = {
            "subscription_id": str(ObjectId()),
            "transaction_id": "TXN-123456789ABC",
            "user_id": "507f1f77bcf86cd799439011",
            "fund_id": 1,
            "fund_name": "FPV_BTG_PACTUAL_RECAUDADORA",
            "amount": 75000.0,
            "previous_balance": 500000.0,
            "new_balance": 425000.0,
            "notification_sent": True,
            "notification_type": "email",
            "message": "Suscripción exitosa",
            "created_at": datetime.now(timezone.utc)
        }
        
        with patch('app.routers.subscriptions.TransactionService.subscribe_to_fund', AsyncMock(return_value=mock_result)):
            response = await async_client.post(
                "/api/v1/subscriptions",
                json=subscription_data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["fund_id"] == 1
            assert data["new_balance"] == 425000.0
    
    @pytest.mark.asyncio
    async def test_cancel_subscription_success(self, async_client, auth_headers):
        """Test cancelación exitosa de suscripción."""
        subscription_id = str(ObjectId())
        
        mock_result = {
            "subscription_id": subscription_id,
            "transaction_id": "TXN-987654321DEF",
            "user_id": "507f1f77bcf86cd799439011",
            "fund_id": 1,
            "fund_name": "FPV_BTG_PACTUAL_RECAUDADORA",
            "amount_returned": 75000.0,
            "previous_balance": 425000.0,
            "new_balance": 500000.0,
            "notification_sent": True,
            "message": "Cancelación exitosa",
            "cancelled_at": datetime.now(timezone.utc)
        }
        
        with patch('app.routers.subscriptions.TransactionService.cancel_subscription', AsyncMock(return_value=mock_result)):
            response = await async_client.delete(
                f"/api/v1/subscriptions/{subscription_id}",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["amount_returned"] == 75000.0
            assert data["new_balance"] == 500000.0
    
    @pytest.mark.asyncio
    async def test_get_transaction_history(self, async_client, auth_headers):
        """Test obtener historial de transacciones."""
        mock_result = {
            "user_id": "507f1f77bcf86cd799439011",
            "transactions": [],
            "total": 0,
            "page": 1,
            "page_size": 10,
            "total_pages": 1
        }
        
        with patch('app.routers.subscriptions.TransactionService.get_transaction_history', AsyncMock(return_value=mock_result)):
            response = await async_client.get(
                "/api/v1/subscriptions/history",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "transactions" in data
            assert data["page"] == 1


class TestHealthEndpoints:
    """Pruebas para endpoints de health."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client):
        """Test endpoint raíz."""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["status"] == "running"
