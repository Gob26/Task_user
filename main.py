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

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:                #получение сессии
        yield session


@app.post("/tasks/", response_model=schemas.Task)
async def create_task(task: schemas.TaskCreate, user_id, db: AsyncSession = Depends(get_db)):
    return await crud.create_task(db=db, task=task, user_id=user_id)

@app.get("/tasks/", response_model=list[schemas.Task])
async def read_tasks(user_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_tasks_user(db=db, user_id=user_id)

@app.get("/tasks/all/", response_model=list[schemas.Task])
async def read_all_tasks(db: AsyncSession = Depends(get_db)):
    return await crud.get_tasks_all(db=db)

@app.get("tasks/{task_id}", response_model=schemas.Task)
async def read_task(task_id: int, db: AsyncSession = Depends(get_db)):
    db_task = await crud.get_task(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Таблица не найдена")
    return db_task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
async def update_task(task_id: int, task: schemas.TaskUpdate, db: AsyncSession = Depends(get_db)):
    db_task = await crud.get_task(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Таблица не найдена")
    return await crud.update_task(db=db, task_id=task_id, task=task)

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await crud.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Таблица не найдена")
    await crud.delete_task(db=db, task_id=task_id)
    return {"message": "Задача удалена"}