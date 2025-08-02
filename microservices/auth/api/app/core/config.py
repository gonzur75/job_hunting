from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path=Path("../.envs/.env"))


class Settings(BaseSettings):
    POSTGRES_USER: str = Field(..., alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., alias="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., alias="POSTGRES_DB")
    POSTGRES_PORT: int = Field(5432, alias="POSTGRES_PORT")
    POSTGRES_HOST: str = Field(..., alias="POSTGRES_HOST")
    POSTGRES_ASYNC_DRIVER: str = "postgresql+asyncpg://"
    POSTGRES_SYNC_DRIVER: str = "postgresql+psycopg://"

    SECRET_KEY: str = Field(..., alias="SECRET_KEY")
    SALT_EMAIL: str = Field(..., alias="SALT_EMAIL")

    JWT_PRIVATE_KEY: str = Field(..., alias="JWT_PRIVATE_KEY")
    JWT_PUBLIC_KEY: str = Field(..., alias="JWT_PUBLIC_KEY")
    JWT_ALGORITHM: str = Field("RS256", alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def JWT_PRIVATE_KEY_PEM(self) -> str:
        return self.JWT_PRIVATE_KEY.replace("\\n", "\n")

    @property
    def JWT_PUBLIC_KEY_PEM(self) -> str:
        return self.JWT_PUBLIC_KEY.replace("\\n", "\n")


settings = Settings()  # type: ignore
