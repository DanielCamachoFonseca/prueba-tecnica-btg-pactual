"""
Pruebas unitarias para el servicio de usuarios.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from bson import ObjectId

from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.core.exceptions import UserNotFoundException, UserAlreadyExistsException
from app.models.user import NotificationPreference


class TestUserService:
    """Pruebas para UserService."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Test crear usuario exitosamente."""
        user_data = UserCreate(
            email="nuevo@btgpactual.com",
            password="Password123",
            full_name="Nuevo Usuario",
            phone="+573001234567",
            notification_preference=NotificationPreference.EMAIL
        )
        
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=ObjectId())
        )
        
        with patch.object(UserService, 'get_collection', return_value=mock_collection):
            result = await UserService.create_user(user_data)
            
            assert result["email"] == user_data.email
            assert result["full_name"] == user_data.full_name
            assert result["balance"] == 500000.0
            assert "hashed_password" in result
            mock_collection.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_already_exists(self):
        """Test error al crear usuario con email existente."""
        user_data = UserCreate(
            email="existente@btgpactual.com",
            password="Password123",
            full_name="Usuario Existente"
        )
        
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value={"email": user_data.email})
        
        with patch.object(UserService, 'get_collection', return_value=mock_collection):
            with pytest.raises(UserAlreadyExistsException):
                await UserService.create_user(user_data)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self):
        """Test obtener usuario por ID exitosamente."""
        user_id = str(ObjectId())
        mock_user = {
            "_id": ObjectId(user_id),
            "email": "test@btgpactual.com",
            "full_name": "Test User",
            "balance": 500000.0
        }
        
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=mock_user)
        
        with patch.object(UserService, 'get_collection', return_value=mock_collection):
            result = await UserService.get_user_by_id(user_id)
            
            assert result["email"] == mock_user["email"]
            assert result["_id"] == user_id
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Test error cuando usuario no existe."""
        user_id = str(ObjectId())
        
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        
        with patch.object(UserService, 'get_collection', return_value=mock_collection):
            with pytest.raises(UserNotFoundException):
                await UserService.get_user_by_id(user_id)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_invalid_id(self):
        """Test error con ID inválido."""
        mock_collection = MagicMock()
        
        with patch.object(UserService, 'get_collection', return_value=mock_collection):
            with pytest.raises(UserNotFoundException):
                await UserService.get_user_by_id("invalid_id")
    
    @pytest.mark.asyncio
    async def test_update_balance(self):
        """Test actualizar saldo de usuario."""
        user_id = str(ObjectId())
        new_balance = 425000.0
        
        mock_user = {
            "_id": ObjectId(user_id),
            "email": "test@btgpactual.com",
            "balance": new_balance
        }
        
        mock_collection = MagicMock()
        mock_collection.update_one = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=mock_user)
        
        with patch.object(UserService, 'get_collection', return_value=mock_collection):
            result = await UserService.update_balance(user_id, new_balance)
            
            assert result["balance"] == new_balance
            mock_collection.update_one.assert_called_once()
