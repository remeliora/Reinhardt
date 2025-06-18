from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Строка подключения
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    # Параметры пула
    DB_POOL_SIZE: int = Field(5, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(10, env="DB_MAX_OVERFLOW")

    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field("reinhardt_monitor.log", env="LOG_FILE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
