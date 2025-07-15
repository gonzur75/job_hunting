from pathlib import Path
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv



load_dotenv(dotenv_path=Path("../envs/.env.db_sql"))


# wymusza typingi do settingsów co umozliwia walidacje prze pydantic
class Settings(BaseSettings):
    POSTGRES_USER: str | None = os.getenv(
        "POSTGRES_USER",
    )
    POSTGRES_PASSWORD: str | None = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str | None = os.getenv(
        "POSTGRES_DB",
    )
    POSTGRES_HOST: str | None = os.getenv(
        "POSTGRES_HOST",
    )
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_ASYNC_DRIVER: str = "postgresql+asyncpg"
    POSTGRES_SYNC_DRIVER: str = "postgresql+psycopg"
    DATABASE_URL: str = (
        f"://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )


settings = Settings()
print(settings.DATABASE_URL)
