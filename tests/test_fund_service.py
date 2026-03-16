"""
Pruebas unitarias para el servicio de fondos.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from bson import ObjectId

from app.services.fund_service import FundService
from app.core.exceptions import FundNotFoundException
from app.models.fund import INITIAL_FUNDS


class TestFundService:
    """Pruebas para FundService."""
    
    @pytest.mark.asyncio
    async def test_get_all_funds(self):
        """Test obtener todos los fondos."""
        mock_funds = [
            {
                "_id": ObjectId(),
                "fund_id": 1,
                "name": "FPV_BTG_PACTUAL_RECAUDADORA",
                "minimum_amount": 75000.0,
                "category": "FPV",
                "is_active": True
            },
            {
                "_id": ObjectId(),
                "fund_id": 2,
                "name": "FPV_BTG_PACTUAL_ECOPETROL",
                "minimum_amount": 125000.0,
                "category": "FPV",
                "is_active": True
            }
        ]
        
        async def mock_cursor():
            for fund in mock_funds:
                yield fund
        
        mock_collection = MagicMock()
        mock_find = MagicMock()
        mock_sort = MagicMock()
        mock_sort.__aiter__ = lambda self: mock_cursor().__aiter__()
        mock_find.sort = MagicMock(return_value=mock_sort)
        mock_collection.find = MagicMock(return_value=mock_find)
        
        with patch.object(FundService, 'get_collection', return_value=mock_collection):
            result = await FundService.get_all_funds()
            
            assert len(result) == 2
            assert result[0]["name"] == "FPV_BTG_PACTUAL_RECAUDADORA"
    
    @pytest.mark.asyncio
    async def test_get_fund_by_id_success(self):
        """Test obtener fondo por ID exitosamente."""
        mock_fund = {
            "_id": ObjectId(),
            "fund_id": 1,
            "name": "FPV_BTG_PACTUAL_RECAUDADORA",
            "minimum_amount": 75000.0,
            "category": "FPV",
            "is_active": True
        }
        
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=mock_fund)
        
        with patch.object(FundService, 'get_collection', return_value=mock_collection):
            result = await FundService.get_fund_by_id(1)
            
            assert result["fund_id"] == 1
            assert result["name"] == "FPV_BTG_PACTUAL_RECAUDADORA"
            assert result["minimum_amount"] == 75000.0
    
    @pytest.mark.asyncio
    async def test_get_fund_by_id_not_found(self):
        """Test error cuando fondo no existe."""
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=None)
        
        with patch.object(FundService, 'get_collection', return_value=mock_collection):
            with pytest.raises(FundNotFoundException):
                await FundService.get_fund_by_id(999)
    
    @pytest.mark.asyncio
    async def test_get_fund_minimum_amount(self):
        """Test obtener monto mínimo de un fondo."""
        mock_fund = {
            "_id": ObjectId(),
            "fund_id": 3,
            "name": "DEUDAPRIVADA",
            "minimum_amount": 50000.0,
            "category": "FIC",
            "is_active": True
        }
        
        mock_collection = MagicMock()
        mock_collection.find_one = AsyncMock(return_value=mock_fund)
        
        with patch.object(FundService, 'get_collection', return_value=mock_collection):
            result = await FundService.get_fund_minimum_amount(3)
            
            assert result == 50000.0
    
    def test_initial_funds_data(self):
        """Test que los fondos iniciales tienen la estructura correcta."""
        assert len(INITIAL_FUNDS) == 5
        
        for fund in INITIAL_FUNDS:
            assert "fund_id" in fund
            assert "name" in fund
            assert "minimum_amount" in fund
            assert "category" in fund
            assert fund["minimum_amount"] > 0
