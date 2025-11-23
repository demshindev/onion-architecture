from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from src.infrastructure.constants import DatabaseConstants


class Settings(BaseSettings):
    database_url: str = Field(default="mysql+aiomysql://user:password@localhost:3306/dbname?charset=utf8mb4")
    debug: bool = Field(default=False)
    
    api_title: str = "Test API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    database_pool_size: int = DatabaseConstants.DEFAULT_POOL_SIZE
    database_max_overflow: int = DatabaseConstants.DEFAULT_MAX_OVERFLOW
    database_pool_pre_ping: bool = True

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError("Database URL cannot be empty")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

