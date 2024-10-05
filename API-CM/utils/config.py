from pydantic_settings import BaseSettings
from functools import lru_cache
import os
#  This file is used for read .env file

class Settings(BaseSettings):
    APP_NAME: str = "Catalyst Media"
    DB_HOSTNAME: str
    DB_SCHEMANAME: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_PORT: int
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    TOKEN_EXPIRE_MINUTES: int
    VERSION: str
    ENV: str
    INSTANCE_ID: str
    FILE_LOG_DIR: str
    PROJECT_FILE_DIR: str = os.path.join(os.getcwd(), "static/files")

    

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    settings = Settings()
    return settings


# settings = get_settings()
