from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


class FundCategory(str, Enum):
    FPV = "FPV"
    FIC = "FIC"


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class FundModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    fund_id: int = Field(..., ge=1)
    name: str
    minimum_amount: float = Field(..., ge=0)
    category: FundCategory
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


INITIAL_FUNDS = [
    {
        "fund_id": 1,
        "name": "FPV_BTG_PACTUAL_RECAUDADORA",
        "minimum_amount": 75000.0,
        "category": FundCategory.FPV,
        "description": "Fondo de Pensiones Voluntarias BTG Pactual Recaudadora"
    },
    {
        "fund_id": 2,
        "name": "FPV_BTG_PACTUAL_ECOPETROL",
        "minimum_amount": 125000.0,
        "category": FundCategory.FPV,
        "description": "Fondo de Pensiones Voluntarias BTG Pactual Ecopetrol"
    },
    {
        "fund_id": 3,
        "name": "DEUDAPRIVADA",
        "minimum_amount": 50000.0,
        "category": FundCategory.FIC,
        "description": "Fondo de Inversión Colectiva Deuda Privada"
    },
    {
        "fund_id": 4,
        "name": "FDO-ACCIONES",
        "minimum_amount": 250000.0,
        "category": FundCategory.FIC,
        "description": "Fondo de Inversión Colectiva Acciones"
    },
    {
        "fund_id": 5,
        "name": "FPV_BTG_PACTUAL_DINAMICA",
        "minimum_amount": 100000.0,
        "category": FundCategory.FPV,
        "description": "Fondo de Pensiones Voluntarias BTG Pactual Dinámica"
    }
]
