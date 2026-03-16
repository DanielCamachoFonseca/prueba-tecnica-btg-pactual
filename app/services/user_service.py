from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
import logging

from app.core.database import get_collection
from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import UserRole, NotificationPreference

logger = logging.getLogger(__name__)
COLLECTION_NAME = "users"


class UserService:
    @staticmethod
    def get_collection():
        return get_collection(COLLECTION_NAME)
    
    @classmethod
    async def create_user(cls, user_data: UserCreate) -> Dict[str, Any]:
        collection = cls.get_collection()
        
        existing_user = await collection.find_one({"email": user_data.email})
        if existing_user:
            raise UserAlreadyExistsException(user_data.email)
        
        user_doc = {
            "email": user_data.email,
            "hashed_password": get_password_hash(user_data.password),
            "full_name": user_data.full_name,
            "phone": user_data.phone,
            "balance": settings.INITIAL_CLIENT_BALANCE,
            "notification_preference": user_data.notification_preference.value,
            "role": UserRole.CLIENT.value,
            "is_active": True,
            "subscriptions": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        result = await collection.insert_one(user_doc)
        user_doc["_id"] = str(result.inserted_id)
        
        logger.info(f"Usuario creado: {user_data.email}")
        return user_doc
    
    @classmethod
    async def get_user_by_id(cls, user_id: str) -> Dict[str, Any]:
        collection = cls.get_collection()
        
        if not ObjectId.is_valid(user_id):
            raise UserNotFoundException(user_id)
        
        user = await collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise UserNotFoundException(user_id)
        
        user["_id"] = str(user["_id"])
        return user
    
    @classmethod
    async def get_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        collection = cls.get_collection()
        user = await collection.find_one({"email": email})
        
        if user:
            user["_id"] = str(user["_id"])
        
        return user
    
    @classmethod
    async def authenticate_user(cls, email: str, password: str) -> Dict[str, Any]:
        user = await cls.get_user_by_email(email)
        
        if not user:
            raise InvalidCredentialsException()
        
        if not verify_password(password, user["hashed_password"]):
            raise InvalidCredentialsException()
        
        if not user.get("is_active", True):
            raise InvalidCredentialsException()
        
        logger.info(f"Usuario autenticado: {email}")
        return user
    
    @classmethod
    async def update_user(cls, user_id: str, user_update: UserUpdate) -> Dict[str, Any]:
        collection = cls.get_collection()
        
        await cls.get_user_by_id(user_id)
        
        update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
        
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            
            if "notification_preference" in update_data:
                update_data["notification_preference"] = update_data["notification_preference"].value
            
            await collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
        
        return await cls.get_user_by_id(user_id)
    
    @classmethod
    async def update_balance(cls, user_id: str, new_balance: float) -> Dict[str, Any]:
        collection = cls.get_collection()
        
        await collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "balance": new_balance,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return await cls.get_user_by_id(user_id)
    
    @classmethod
    async def get_user_balance(cls, user_id: str) -> float:
        user = await cls.get_user_by_id(user_id)
        return user.get("balance", 0.0)
    
    @classmethod
    async def add_subscription_to_user(cls, user_id: str, subscription_id: str) -> None:
        collection = cls.get_collection()
        
        await collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$push": {"subscriptions": subscription_id},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
    
    @classmethod
    async def remove_subscription_from_user(cls, user_id: str, subscription_id: str) -> None:
        collection = cls.get_collection()
        
        await collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$pull": {"subscriptions": subscription_id},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
