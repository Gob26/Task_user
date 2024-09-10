from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, async_session
from config import settings
from database import database, Base
import crud
import schemas

engine = create_async_engine(settings.DATABASE_URL_asyncpg, echo=True)       # асинхронный Движок
async_sessionmaker = async_sessionmaker(                                     # асинхронная сессия
    engine, class_=AsyncSession,
    expire_on_commit=False)                       # Отключаем авто-обновление данных после комита

app = FastAPI()




