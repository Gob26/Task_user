from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncSession
from config import settings


app = FastAPI()

DATABASE_URL_asyncpg = settings.DATABASE_URL_asyncpg()
engine = create_async_engine(
    DATABASE_URL_asyncpg,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True                     #Проверка устаревших соединений
)