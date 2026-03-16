from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "BTG Pactual Funds API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # MongoDB
    MONGODB_URL: str = "mongodb://btg_admin:btg_secure_password_2024@localhost:27017"
    MONGODB_DATABASE: str = "btg_funds"
    
    # JWT Security
    SECRET_KEY: str = "btg-pactual-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Business Rules
    INITIAL_CLIENT_BALANCE: float = 500000.0  # COP $500.000
    
    # Notifications (simuladas para desarrollo)
    NOTIFICATION_EMAIL_ENABLED: bool = True
    NOTIFICATION_SMS_ENABLED: bool = True
    
    # AWS (para producción)
    AWS_REGION: str = "us-east-1"
    AWS_SNS_TOPIC_ARN: str = ""
    AWS_SES_SENDER_EMAIL: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
