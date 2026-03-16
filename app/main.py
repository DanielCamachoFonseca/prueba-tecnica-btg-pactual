from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from app.core.config import settings
from app.core.database import Database
from app.core.exceptions import BTGException
from app.services.fund_service import FundService
from app.routers import auth, funds, subscriptions, users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando BTG Pactual Funds API...")
    
    try:
        # Conectar a MongoDB
        await Database.connect()
        
        # Inicializar fondos predefinidos
        await FundService.initialize_funds()
        
        logger.info("API iniciada correctamente")
    except Exception as e:
        logger.error(f"Error durante el inicio: {e}")
        raise
    
    yield
    
    logger.info("Cerrando BTG Pactual Funds API...")
    await Database.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## BTG Pactual Funds API
    
    API REST para gestión de fondos de inversión de BTG Pactual.
    
    ### Funcionalidades:
    
    * **Autenticación**: Registro e inicio de sesión con JWT
    * **Fondos**: Consulta de fondos disponibles
    * **Suscripciones**: Apertura y cancelación de fondos
    * **Historial**: Consulta de transacciones
    * **Notificaciones**: Email/SMS según preferencia del usuario
    
    ### Reglas de Negocio:
    
    * Saldo inicial del cliente: **COP $500.000**
    * Cada fondo tiene un monto mínimo de vinculación
    * Al cancelar, el monto se devuelve al saldo del cliente
    
    ### Fondos Disponibles:
    
    | ID | Nombre | Monto Mínimo | Categoría |
    |----|--------|--------------|-----------|
    | 1 | FPV_BTG_PACTUAL_RECAUDADORA | $75.000 | FPV |
    | 2 | FPV_BTG_PACTUAL_ECOPETROL | $125.000 | FPV |
    | 3 | DEUDAPRIVADA | $50.000 | FIC |
    | 4 | FDO-ACCIONES | $250.000 | FIC |
    | 5 | FPV_BTG_PACTUAL_DINAMICA | $100.000 | FPV |
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BTGException)
async def btg_exception_handler(request: Request, exc: BTGException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
            "success": False
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Error de validación en los datos enviados",
            "errors": errors,
            "success": False
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no controlado: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Error interno del servidor",
            "error_code": "INTERNAL_ERROR",
            "success": False
        }
    )


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(funds.router, prefix=settings.API_V1_PREFIX)
app.include_router(subscriptions.router, prefix=settings.API_V1_PREFIX)


@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
    description="Endpoint raíz con información de la API"
)
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Verifica el estado de la API y la conexión a la base de datos"
)
async def health_check():
    try:
        db = Database.get_database()
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
