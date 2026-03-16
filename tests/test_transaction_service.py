"""
Pruebas unitarias para el servicio de transacciones.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from bson import ObjectId

from app.services.transaction_service import TransactionService
from app.core.exceptions import (
    InsufficientBalanceException,
    AlreadySubscribedException,
    SubscriptionNotFoundException
)


class TestTransactionService:
    """Pruebas para TransactionService."""
    
    @pytest.mark.asyncio
    async def test_subscribe_to_fund_success(self):
        """Test suscripción exitosa a un fondo."""
        user_id = str(ObjectId())
        fund_id = 1
        
        mock_user = {
            "_id": user_id,
            "email": "test@btgpactual.com",
            "balance": 500000.0,
            "notification_preference": "email",
            "phone": None
        }
        
        mock_fund = {
            "_id": str(ObjectId()),
            "fund_id": 1,
            "name": "FPV_BTG_PACTUAL_RECAUDADORA",
            "minimum_amount": 75000.0,
            "is_active": True
        }
        
        mock_subscriptions_col = MagicMock()
        mock_subscriptions_col.find_one = AsyncMock(return_value=None)
        mock_subscriptions_col.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=ObjectId())
        )
        
        mock_transactions_col = MagicMock()
        mock_transactions_col.insert_one = AsyncMock()
        mock_transactions_col.update_one = AsyncMock()
        
        with patch.object(TransactionService, 'get_subscriptions_collection', return_value=mock_subscriptions_col), \
             patch.object(TransactionService, 'get_transactions_collection', return_value=mock_transactions_col), \
             patch('app.services.transaction_service.UserService.get_user_by_id', AsyncMock(return_value=mock_user)), \
             patch('app.services.transaction_service.UserService.update_balance', AsyncMock()), \
             patch('app.services.transaction_service.UserService.add_subscription_to_user', AsyncMock()), \
             patch('app.services.transaction_service.FundService.get_fund_by_id', AsyncMock(return_value=mock_fund)), \
             patch('app.services.transaction_service.NotificationService.send_subscription_notification', AsyncMock(return_value=(True, "email"))):
            
            result = await TransactionService.subscribe_to_fund(user_id, fund_id)
            
            assert result["fund_id"] == fund_id
            assert result["fund_name"] == "FPV_BTG_PACTUAL_RECAUDADORA"
            assert result["amount"] == 75000.0
            assert result["previous_balance"] == 500000.0
            assert result["new_balance"] == 425000.0
            assert result["notification_sent"] is True
    
    @pytest.mark.asyncio
    async def test_subscribe_insufficient_balance(self):
        """Test error por saldo insuficiente."""
        user_id = str(ObjectId())
        fund_id = 4  # FDO-ACCIONES con mínimo de 250.000
        
        mock_user = {
            "_id": user_id,
            "email": "test@btgpactual.com",
            "balance": 100000.0,  # Saldo insuficiente
            "notification_preference": "email"
        }
        
        mock_fund = {
            "_id": str(ObjectId()),
            "fund_id": 4,
            "name": "FDO-ACCIONES",
            "minimum_amount": 250000.0,
            "is_active": True
        }
        
        mock_subscriptions_col = MagicMock()
        mock_subscriptions_col.find_one = AsyncMock(return_value=None)
        
        mock_transactions_col = MagicMock()
        
        with patch.object(TransactionService, 'get_subscriptions_collection', return_value=mock_subscriptions_col), \
             patch.object(TransactionService, 'get_transactions_collection', return_value=mock_transactions_col), \
             patch('app.services.transaction_service.UserService.get_user_by_id', AsyncMock(return_value=mock_user)), \
             patch('app.services.transaction_service.FundService.get_fund_by_id', AsyncMock(return_value=mock_fund)):
            
            with pytest.raises(InsufficientBalanceException) as exc_info:
                await TransactionService.subscribe_to_fund(user_id, fund_id)
            
            assert "FDO-ACCIONES" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_subscribe_already_subscribed(self):
        """Test error cuando ya está suscrito al fondo."""
        user_id = str(ObjectId())
        fund_id = 1
        
        mock_user = {
            "_id": user_id,
            "email": "test@btgpactual.com",
            "balance": 500000.0
        }
        
        mock_fund = {
            "_id": str(ObjectId()),
            "fund_id": 1,
            "name": "FPV_BTG_PACTUAL_RECAUDADORA",
            "minimum_amount": 75000.0,
            "is_active": True
        }
        
        # Suscripción existente activa
        mock_existing_subscription = {
            "_id": ObjectId(),
            "user_id": user_id,
            "fund_id": 1,
            "is_active": True
        }
        
        mock_subscriptions_col = MagicMock()
        mock_subscriptions_col.find_one = AsyncMock(return_value=mock_existing_subscription)
        
        mock_transactions_col = MagicMock()
        
        with patch.object(TransactionService, 'get_subscriptions_collection', return_value=mock_subscriptions_col), \
             patch.object(TransactionService, 'get_transactions_collection', return_value=mock_transactions_col), \
             patch('app.services.transaction_service.UserService.get_user_by_id', AsyncMock(return_value=mock_user)), \
             patch('app.services.transaction_service.FundService.get_fund_by_id', AsyncMock(return_value=mock_fund)):
            
            with pytest.raises(AlreadySubscribedException):
                await TransactionService.subscribe_to_fund(user_id, fund_id)
    
    @pytest.mark.asyncio
    async def test_cancel_subscription_success(self):
        """Test cancelación exitosa de suscripción."""
        user_id = str(ObjectId())
        subscription_id = str(ObjectId())
        
        mock_user = {
            "_id": user_id,
            "email": "test@btgpactual.com",
            "balance": 425000.0,
            "notification_preference": "email",
            "phone": None
        }
        
        mock_subscription = {
            "_id": ObjectId(subscription_id),
            "user_id": user_id,
            "fund_id": 1,
            "fund_name": "FPV_BTG_PACTUAL_RECAUDADORA",
            "amount": 75000.0,
            "is_active": True
        }
        
        mock_subscriptions_col = MagicMock()
        mock_subscriptions_col.find_one = AsyncMock(return_value=mock_subscription)
        mock_subscriptions_col.update_one = AsyncMock()
        
        mock_transactions_col = MagicMock()
        mock_transactions_col.insert_one = AsyncMock()
        mock_transactions_col.update_one = AsyncMock()
        
        with patch.object(TransactionService, 'get_subscriptions_collection', return_value=mock_subscriptions_col), \
             patch.object(TransactionService, 'get_transactions_collection', return_value=mock_transactions_col), \
             patch('app.services.transaction_service.UserService.get_user_by_id', AsyncMock(return_value=mock_user)), \
             patch('app.services.transaction_service.UserService.update_balance', AsyncMock()), \
             patch('app.services.transaction_service.UserService.remove_subscription_from_user', AsyncMock()), \
             patch('app.services.transaction_service.NotificationService.send_cancellation_notification', AsyncMock(return_value=(True, "email"))):
            
            result = await TransactionService.cancel_subscription(user_id, subscription_id)
            
            assert result["subscription_id"] == subscription_id
            assert result["amount_returned"] == 75000.0
            assert result["previous_balance"] == 425000.0
            assert result["new_balance"] == 500000.0
    
    @pytest.mark.asyncio
    async def test_cancel_subscription_not_found(self):
        """Test error cuando suscripción no existe."""
        user_id = str(ObjectId())
        subscription_id = str(ObjectId())
        
        mock_subscriptions_col = MagicMock()
        mock_subscriptions_col.find_one = AsyncMock(return_value=None)
        
        mock_transactions_col = MagicMock()
        
        with patch.object(TransactionService, 'get_subscriptions_collection', return_value=mock_subscriptions_col), \
             patch.object(TransactionService, 'get_transactions_collection', return_value=mock_transactions_col):
            with pytest.raises(SubscriptionNotFoundException):
                await TransactionService.cancel_subscription(user_id, subscription_id)
    
    @pytest.mark.asyncio
    async def test_get_transaction_history(self):
        """Test obtener historial de transacciones."""
        user_id = str(ObjectId())
        
        mock_transactions = [
            {
                "_id": ObjectId(),
                "transaction_id": "TXN-123456789ABC",
                "user_id": user_id,
                "fund_id": 1,
                "fund_name": "FPV_BTG_PACTUAL_RECAUDADORA",
                "transaction_type": "apertura",
                "amount": 75000.0,
                "status": "completada",
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        async def mock_cursor():
            for txn in mock_transactions:
                yield txn
        
        mock_transactions_col = MagicMock()
        mock_transactions_col.count_documents = AsyncMock(return_value=1)
        
        mock_find = MagicMock()
        mock_sort = MagicMock()
        mock_skip = MagicMock()
        mock_limit = MagicMock()
        mock_limit.__aiter__ = lambda self: mock_cursor().__aiter__()
        mock_skip.limit = MagicMock(return_value=mock_limit)
        mock_sort.skip = MagicMock(return_value=mock_skip)
        mock_find.sort = MagicMock(return_value=mock_sort)
        mock_transactions_col.find = MagicMock(return_value=mock_find)
        
        with patch.object(TransactionService, 'get_transactions_collection', return_value=mock_transactions_col):
            result = await TransactionService.get_transaction_history(user_id)
            
            assert result["user_id"] == user_id
            assert result["total"] == 1
            assert len(result["transactions"]) == 1
            assert result["transactions"][0]["transaction_type"] == "apertura"
