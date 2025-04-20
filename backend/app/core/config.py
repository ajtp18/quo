from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    PROJECT_NAME: str = "Banking API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MIN_BLACKLIST_TIME: int = 3600
    
    # Database
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: Optional[str] = None

    # Redis keys prefixes
    REDIS_REFRESH_TOKEN_KEY_PREFIX: str = "refresh_tokens:"
    REDIS_BLACKLIST_KEY_PREFIX: str = "blacklist:"

    # Belvo
    BELVO_SECRET_ID: str
    BELVO_SECRET_PASSWORD: str
    BELVO_API_URL: str = "https://sandbox.belvo.com"
    BELVO_DEFAULT_USERNAME: str = "12345678901"
    BELVO_DEFAULT_PASSWORD: str = "123456"

    # Default credentials por tipo de institución
    BANK_DEFAULT_USERNAME: str = "user123"
    BANK_DEFAULT_PASSWORD: str = "pass123"
    
    EMPLOYMENT_DEFAULT_DOCUMENT: str = "BLPM951331IONVGR54"
    EMPLOYMENT_DEFAULT_EMAIL: str = "default@example.com"
    EMPLOYMENT_DEFAULT_PASSWORD: str = "pass123"
    
    FISCAL_DEFAULT_RFC: str = "XAXX010101000"
    FISCAL_DEFAULT_PASSWORD: str = "pass123"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 