from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Ardhnarishwar AI Robotics Interview Platform"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "ardhnarishwar_super_secret_jwt_key_change_in_production_2026!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ardhnarishwar.db"
    
    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Storage
    STORAGE_PROVIDER: str = "local"  # "local", "s3", "minio", "r2"
    STORAGE_ENDPOINT: str = "http://localhost:9000"
    STORAGE_BUCKET: str = "ardhnarishwar-recordings"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_REGION: str = "us-east-1"
    STORAGE_LOCAL_DIR: str = "./storage_data"

    # AI Engine
    EVALUATION_ENGINE_VERSION: str = "internal-v1"

    # Super Admin Defaults for initial seed
    SUPER_ADMIN_EMAIL: str = "admin@ardhnarishwar.ai"
    SUPER_ADMIN_PASSWORD: str = "AdminSecurePassword123!"


settings = Settings()
