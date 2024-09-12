from logging.config import fileConfig

from pydantic_settings import BaseSettings
from pydantic_settings import BaseSettings
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from alembic import context


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    class Config:
        env_file = ".env"

settings = Settings()

# проверка подключения
#db_url = settings.DATABASE_URL_asyncpg
#print(db_url)
