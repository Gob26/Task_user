from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncSession
from config import settings


engine = create_async_engine(settings.DATABASE_URL_asyncpg, echo=True)       # Движок
async_sessionmaker = async_sessionmaker(
    engine, class_=AsyncSession,
    expire_on_commit=False)                       # Отключаем авто-обновление данных после комита

app = FastAPI()
