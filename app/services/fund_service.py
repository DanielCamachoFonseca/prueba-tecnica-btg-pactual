from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
import logging

from app.core.database import get_collection
from app.core.exceptions import FundNotFoundException
from app.schemas.fund import FundCreate, FundUpdate
from app.models.fund import INITIAL_FUNDS

logger = logging.getLogger(__name__)
COLLECTION_NAME = "funds"


class FundService:
    @staticmethod
    def get_collection():
        return get_collection(COLLECTION_NAME)
    
    @classmethod
    async def initialize_funds(cls) -> None:
        collection = cls.get_collection()
        
        for fund_data in INITIAL_FUNDS:
            existing = await collection.find_one({"fund_id": fund_data["fund_id"]})
            
            if not existing:
                fund_doc = {
                    **fund_data,
                    "category": fund_data["category"].value,
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc)
                }
                await collection.insert_one(fund_doc)
                logger.info(f"Fondo creado: {fund_data['name']}")
        
        logger.info("Fondos inicializados correctamente")
    
    @classmethod
    async def get_all_funds(cls, include_inactive: bool = False) -> List[Dict[str, Any]]:
        collection = cls.get_collection()
        
        query = {} if include_inactive else {"is_active": True}
        cursor = collection.find(query).sort("fund_id", 1)
        
        funds = []
        async for fund in cursor:
            fund["_id"] = str(fund["_id"])
            funds.append(fund)
        
        return funds
    
    @classmethod
    async def get_fund_by_id(cls, fund_id: int) -> Dict[str, Any]:
        collection = cls.get_collection()
        fund = await collection.find_one({"fund_id": fund_id})
        
        if not fund:
            raise FundNotFoundException(str(fund_id))
        
        fund["_id"] = str(fund["_id"])
        return fund
    
    @classmethod
    async def get_fund_by_object_id(cls, object_id: str) -> Dict[str, Any]:
        collection = cls.get_collection()
        
        if not ObjectId.is_valid(object_id):
            raise FundNotFoundException(object_id)
        
        fund = await collection.find_one({"_id": ObjectId(object_id)})
        
        if not fund:
            raise FundNotFoundException(object_id)
        
        fund["_id"] = str(fund["_id"])
        return fund
    
    @classmethod
    async def create_fund(cls, fund_data: FundCreate) -> Dict[str, Any]:
        collection = cls.get_collection()
        
        # Verificar si el fund_id ya existe
        existing = await collection.find_one({"fund_id": fund_data.fund_id})
        if existing:
            raise ValueError(f"Ya existe un fondo con ID {fund_data.fund_id}")
        
        fund_doc = {
            **fund_data.model_dump(),
            "category": fund_data.category.value,
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        }
        
        result = await collection.insert_one(fund_doc)
        fund_doc["_id"] = str(result.inserted_id)
        
        logger.info(f"Fondo creado: {fund_data.name}")
        return fund_doc
    
    @classmethod
    async def update_fund(cls, fund_id: int, fund_update: FundUpdate) -> Dict[str, Any]:
        collection = cls.get_collection()
        
        # Verificar que existe
        await cls.get_fund_by_id(fund_id)
        
        update_data = {k: v for k, v in fund_update.model_dump().items() if v is not None}
        
        if update_data:
            if "category" in update_data:
                update_data["category"] = update_data["category"].value
            
            await collection.update_one(
                {"fund_id": fund_id},
                {"$set": update_data}
            )
        
        return await cls.get_fund_by_id(fund_id)
    
    @classmethod
    async def get_fund_minimum_amount(cls, fund_id: int) -> float:
        """
        Obtiene el monto mínimo de un fondo.
        
        Args:
            fund_id: ID del fondo
        
        Returns:
            Monto mínimo de vinculación
        """
        fund = await cls.get_fund_by_id(fund_id)
        return fund.get("minimum_amount", 0.0)
    
    @classmethod
    async def is_fund_active(cls, fund_id: int) -> bool:
        """
        Verifica si un fondo está activo.
        
        Args:
            fund_id: ID del fondo
        
        Returns:
            True si está activo
        """
        fund = await cls.get_fund_by_id(fund_id)
        return fund.get("is_active", False)
