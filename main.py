from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, async_session
from config import settings
from database import database, Base
import crud
import schemas

engine = create_async_engine(settings.DATABASE_URL_asyncpg, echo=True)       # асинхронный движок
async_session_maker = async_sessionmaker(                                     # асинхронная фабрика сессий
    bind=engine, class_=AsyncSession,             #связывает асинхронную сессию с конкретным асинхронным движком
    expire_on_commit=False)                       #отключаем авто-обновление данных после комита


@asynccontextmanager                                          #асинхронный менеджер контекста
async def lifespan(app: FastAPI):                             #управление начальной и завершающей логикой

    async with engine.connect() as conn:                      #не используем
        await conn.run_sync(Base.metadata.create_all)

    await database.connect()                                  #подключение к бд

    try:
        yield
    finally:
        await database.disconnect()                            #отключение от бд


app = FastAPI(lifespan=lifespan)


