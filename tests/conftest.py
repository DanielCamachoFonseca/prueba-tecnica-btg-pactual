"""
Configuración de fixtures para pruebas.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.main import app
from app.core.security import create_access_token
from app.core.config import settings


@pytest.fixture
def test_user_data():
    """Datos de usuario de prueba."""
    return {
        "_id": "507f1f77bcf86cd799439011",
        "email": "test@btgpactual.com",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S9m0c8cVLw4qDi",
        "full_name": "Usuario Test",
        "phone": "+573001234567",
        "balance": 500000.0,
        "notification_preference": "email",
        "role": "client",
        "is_active": True,
        "subscriptions": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def test_fund_data():
    """Datos de fondo de prueba."""
    return {
        "_id": "507f1f77bcf86cd799439012",
        "fund_id": 1,
        "name": "FPV_BTG_PACTUAL_RECAUDADORA",
        "minimum_amount": 75000.0,
        "category": "FPV",
        "description": "Fondo de prueba",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def auth_token(test_user_data):
    """Token de autenticación de prueba."""
    token_data = {
        "sub": test_user_data["_id"],
        "email": test_user_data["email"],
        "role": test_user_data["role"]
    }
    return create_access_token(token_data)


@pytest.fixture
def auth_headers(auth_token):
    """Headers con autorización."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture
async def async_client():
    """Cliente HTTP asíncrono para pruebas."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_database():
    """Mock de la base de datos."""
    with patch('app.core.database.Database') as mock_db:
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock()
        mock_collection.insert_one = AsyncMock()
        mock_collection.update_one = AsyncMock()
        mock_collection.find = MagicMock(return_value=AsyncMock())
        mock_collection.count_documents = AsyncMock(return_value=0)
        
        mock_db.get_collection = MagicMock(return_value=mock_collection)
        mock_db.get_database = MagicMock()
        
        yield mock_db, mock_collection
