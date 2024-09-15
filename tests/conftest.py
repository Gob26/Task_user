from sys import get_asyncgen_hooks
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, NullPool
from config import settings
from main import app, get_db

                                                    # Создание асинхронного движка и фабрики сессий
engine_test = create_async_engine(settings.DATABASE_URL_asyncpg, poolclass=NullPool)
async_session_maker = async_sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)

                                                    #Мета данные для привязки к движку
metadata = MetaData()
metadata.bind = engine_test

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

@pytest.fixture(scope='session')
def event_loop(request):
    """Создание событийного цикла для каждого тестового цикла"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

                                                    # Переопределение зависимости в FastAPI
app.dependency_overrides[get_db] = override_get_async_session

@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)    # Создаем таблицы
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)      # Удаляем таблицы после тестов

#client = TestClient(app)                            # Синхронный клиент

@pytest.fixture(scope='session')                    # Асинхронный клиент
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
