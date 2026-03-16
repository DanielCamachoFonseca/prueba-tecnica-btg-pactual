from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
import logging
import math

from app.core.database import get_collection
from app.core.exceptions import (
    InsufficientBalanceException,
    FundNotFoundException,
    SubscriptionNotFoundException,
    AlreadySubscribedException,
    SubscriptionNotActiveException
)
from app.services.user_service import UserService
from app.services.fund_service import FundService
from app.services.notification_service import NotificationService
from app.models.transaction import (
    TransactionModel,
    SubscriptionModel,
    TransactionType,
    TransactionStatus,
    generate_transaction_id
)
from app.models.user import NotificationPreference

logger = logging.getLogger(__name__)

TRANSACTIONS_COLLECTION = "transactions"
SUBSCRIPTIONS_COLLECTION = "subscriptions"


class TransactionService:
    @staticmethod
    def get_transactions_collection():
        return get_collection(TRANSACTIONS_COLLECTION)
    
    @staticmethod
    def get_subscriptions_collection():
        return get_collection(SUBSCRIPTIONS_COLLECTION)
    
    @classmethod
    async def subscribe_to_fund(cls, user_id: str, fund_id: int) -> Dict[str, Any]:
        subscriptions_col = cls.get_subscriptions_collection()
        transactions_col = cls.get_transactions_collection()
        
        # 1. Obtener datos del usuario y fondo
        user = await UserService.get_user_by_id(user_id)
        fund = await FundService.get_fund_by_id(fund_id)
        
        # 2. Verificar que el fondo esté activo
        if not fund.get("is_active", False):
            raise FundNotFoundException(str(fund_id))
        
        # 3. Verificar que no esté ya suscrito
        existing_subscription = await subscriptions_col.find_one({
            "user_id": user_id,
            "fund_id": fund_id,
            "is_active": True
        })
        
        if existing_subscription:
            raise AlreadySubscribedException(fund["name"])
        
        # 4. Verificar saldo suficiente
        minimum_amount = fund["minimum_amount"]
        current_balance = user["balance"]
        
        if current_balance < minimum_amount:
            raise InsufficientBalanceException(
                fund_name=fund["name"],
                required_amount=minimum_amount,
                available_balance=current_balance
            )
        
        # 5. Calcular nuevo saldo
        new_balance = current_balance - minimum_amount
        
        # 6. Crear suscripción
        subscription_doc = {
            "user_id": user_id,
            "fund_id": fund_id,
            "fund_name": fund["name"],
            "amount": minimum_amount,
            "subscription_date": datetime.now(timezone.utc),
            "is_active": True,
            "cancellation_date": None
        }
        
        subscription_result = await subscriptions_col.insert_one(subscription_doc)
        subscription_id = str(subscription_result.inserted_id)
        
        # 7. Crear transacción
        transaction_id = generate_transaction_id()
        transaction_doc = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "fund_id": fund_id,
            "fund_name": fund["name"],
            "transaction_type": TransactionType.SUBSCRIPTION.value,
            "amount": minimum_amount,
            "status": TransactionStatus.COMPLETED.value,
            "previous_balance": current_balance,
            "new_balance": new_balance,
            "notification_sent": False,
            "notification_type": None,
            "created_at": datetime.now(timezone.utc)
        }
        
        await transactions_col.insert_one(transaction_doc)
        
        # 8. Actualizar saldo del usuario
        await UserService.update_balance(user_id, new_balance)
        await UserService.add_subscription_to_user(user_id, subscription_id)
        
        # 9. Enviar notificación
        notification_preference = NotificationPreference(user.get("notification_preference", "email"))
        notification_sent, notification_type = await NotificationService.send_subscription_notification(
            email=user["email"],
            phone=user.get("phone"),
            preference=notification_preference,
            fund_name=fund["name"],
            amount=minimum_amount,
            transaction_id=transaction_id
        )
        
        # 10. Actualizar transacción con estado de notificación
        await transactions_col.update_one(
            {"transaction_id": transaction_id},
            {"$set": {
                "notification_sent": notification_sent,
                "notification_type": notification_type
            }}
        )
        
        logger.info(f"Suscripción exitosa: Usuario {user_id} -> Fondo {fund['name']}")
        
        return {
            "subscription_id": subscription_id,
            "transaction_id": transaction_id,
            "user_id": user_id,
            "fund_id": fund_id,
            "fund_name": fund["name"],
            "amount": minimum_amount,
            "previous_balance": current_balance,
            "new_balance": new_balance,
            "notification_sent": notification_sent,
            "notification_type": notification_type,
            "message": f"Suscripción exitosa al fondo {fund['name']}",
            "created_at": datetime.now(timezone.utc)
        }
    
    @classmethod
    async def cancel_subscription(cls, user_id: str, subscription_id: str) -> Dict[str, Any]:
        subscriptions_col = cls.get_subscriptions_collection()
        transactions_col = cls.get_transactions_collection()
        
        # 1. Verificar que la suscripción existe y pertenece al usuario
        if not ObjectId.is_valid(subscription_id):
            raise SubscriptionNotFoundException(subscription_id)
        
        subscription = await subscriptions_col.find_one({
            "_id": ObjectId(subscription_id),
            "user_id": user_id
        })
        
        if not subscription:
            raise SubscriptionNotFoundException(subscription_id)
        
        # 2. Verificar que está activa
        if not subscription.get("is_active", False):
            raise SubscriptionNotActiveException(subscription_id)
        
        # 3. Obtener datos del usuario
        user = await UserService.get_user_by_id(user_id)
        current_balance = user["balance"]
        amount_to_return = subscription["amount"]
        new_balance = current_balance + amount_to_return
        
        # 4. Marcar suscripción como inactiva
        await subscriptions_col.update_one(
            {"_id": ObjectId(subscription_id)},
            {"$set": {
                "is_active": False,
                "cancellation_date": datetime.now(timezone.utc)
            }}
        )
        
        # 5. Crear transacción de cancelación
        transaction_id = generate_transaction_id()
        transaction_doc = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "fund_id": subscription["fund_id"],
            "fund_name": subscription["fund_name"],
            "transaction_type": TransactionType.CANCELLATION.value,
            "amount": amount_to_return,
            "status": TransactionStatus.COMPLETED.value,
            "previous_balance": current_balance,
            "new_balance": new_balance,
            "notification_sent": False,
            "notification_type": None,
            "created_at": datetime.now(timezone.utc)
        }
        
        await transactions_col.insert_one(transaction_doc)
        
        # 6. Actualizar saldo del usuario
        await UserService.update_balance(user_id, new_balance)
        await UserService.remove_subscription_from_user(user_id, subscription_id)
        
        # 7. Enviar notificación
        notification_preference = NotificationPreference(user.get("notification_preference", "email"))
        notification_sent, notification_type = await NotificationService.send_cancellation_notification(
            email=user["email"],
            phone=user.get("phone"),
            preference=notification_preference,
            fund_name=subscription["fund_name"],
            amount=amount_to_return,
            transaction_id=transaction_id
        )
        
        # 8. Actualizar transacción con estado de notificación
        await transactions_col.update_one(
            {"transaction_id": transaction_id},
            {"$set": {
                "notification_sent": notification_sent,
                "notification_type": notification_type
            }}
        )
        
        logger.info(f"Cancelación exitosa: Usuario {user_id} <- Fondo {subscription['fund_name']}")
        
        return {
            "subscription_id": subscription_id,
            "transaction_id": transaction_id,
            "user_id": user_id,
            "fund_id": subscription["fund_id"],
            "fund_name": subscription["fund_name"],
            "amount_returned": amount_to_return,
            "previous_balance": current_balance,
            "new_balance": new_balance,
            "notification_sent": notification_sent,
            "message": f"Cancelación exitosa del fondo {subscription['fund_name']}",
            "cancelled_at": datetime.now(timezone.utc)
        }
    
    @classmethod
    async def get_transaction_history(
        cls,
        user_id: str,
        transaction_type: Optional[TransactionType] = None,
        fund_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        transactions_col = cls.get_transactions_collection()
        
        # Construir query
        query = {"user_id": user_id}
        
        if transaction_type:
            query["transaction_type"] = transaction_type.value
        
        if fund_id:
            query["fund_id"] = fund_id
        
        # Contar total
        total = await transactions_col.count_documents(query)
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        
        # Obtener transacciones paginadas
        skip = (page - 1) * page_size
        cursor = transactions_col.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        
        transactions = []
        async for txn in cursor:
            txn["_id"] = str(txn["_id"])
            transactions.append(txn)
        
        return {
            "user_id": user_id,
            "transactions": transactions,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    @classmethod
    async def get_user_active_subscriptions(cls, user_id: str) -> Dict[str, Any]:
        subscriptions_col = cls.get_subscriptions_collection()
        
        cursor = subscriptions_col.find({
            "user_id": user_id,
            "is_active": True
        }).sort("subscription_date", -1)
        
        subscriptions = []
        total_invested = 0.0
        
        async for sub in cursor:
            sub["_id"] = str(sub["_id"])
            subscriptions.append(sub)
            total_invested += sub["amount"]
        
        user = await UserService.get_user_by_id(user_id)
        
        return {
            "user_id": user_id,
            "subscriptions": subscriptions,
            "total_invested": total_invested,
            "available_balance": user["balance"]
        }
    
    @classmethod
    async def get_subscription_by_id(cls, subscription_id: str) -> Dict[str, Any]:
        subscriptions_col = cls.get_subscriptions_collection()
        
        if not ObjectId.is_valid(subscription_id):
            raise SubscriptionNotFoundException(subscription_id)
        
        subscription = await subscriptions_col.find_one({"_id": ObjectId(subscription_id)})
        
        if not subscription:
            raise SubscriptionNotFoundException(subscription_id)
        
        subscription["_id"] = str(subscription["_id"])
        return subscription
