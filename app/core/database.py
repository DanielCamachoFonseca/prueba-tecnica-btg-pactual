from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls) -> None:
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.database = cls.client[settings.MONGODB_DATABASE]
            
            # Verificar conexión
            await cls.client.admin.command('ping')
            logger.info(f"Conectado exitosamente a MongoDB: {settings.MONGODB_DATABASE}")
        except Exception as e:
            logger.error(f"Error conectando a MongoDB: {e}")
            raise
    
    @classmethod
    async def disconnect(cls) -> None:
        if cls.client:
            cls.client.close()
            logger.info("Desconectado de MongoDB")
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        if cls.database is None:
            raise Exception("Database not initialized. Call connect() first.")
        return cls.database
    
    @classmethod
    def get_collection(cls, collection_name: str):
        return cls.get_database()[collection_name]


def get_database() -> AsyncIOMotorDatabase:
    return Database.get_database()


def get_collection(collection_name: str):
    return Database.get_collection(collection_name)
