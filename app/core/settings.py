from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine

# Resolve .env file relative to this settings file
ENV_FILE = Path(__file__).resolve().parent / "../../env/.env"

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    model_config = SettingsConfigDict(
        # env_file=ENV_FILE.read_text(),
        env_file=str(ENV_FILE),
        extra="ignore"
    )

settings = Settings()