from async_lru import alru_cache     #кеширование
from dns.e164 import query
from sqlalchemy import select, delete
from websockets.version import commit

import schemas
from schemas import TaskUpdate, TaskCreate, UserCreate, UserUpdate
from models import Task, User
from sqlalchemy.ext.asyncio import AsyncSession


async def create_task(db: AsyncSession, task: TaskCreate, user_id: int):  # Убедитесь, что user_id присутствует в аргументах
    db_task = Task(**task.model_dump(), user_id=user_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    # Очистка кэша после создания задачи
    task_to_schema.cache_clear()
    get_tasks_user.cache_clear()
    get_tasks_all.cache_clear()
    return db_task


async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    user_to_schema.cache_clear()
    get_all_users.cache_clear()
    return db_user


@alru_cache(maxsize=128)
async def user_to_schema(db: AsyncSession, user: User) -> schemas.User:
    return schemas.User(
        id=user.id,
        name=user.name,
        surname=user.surname
    )

@alru_cache(maxsize=128)
async def get_all_users(db: AsyncSession):
    query = select(User)
    result = await db.execute(query)
    return result.scalars().all()

                                                                        #декоратор для кеширования async_lru
@alru_cache(maxsize=128)
async def get_tasks_user(db: AsyncSession, user_id: int):              # Получение списка задач для пользователя
    query = select(Task).filter(Task.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()                                      #scalars для простых типов данных

                                                                        # декоратор для кеширования async_lru
@alru_cache(maxsize=128)
async def get_tasks_all(db: AsyncSession):                             #Получение всех задач с указанием пользователей
    query = select(Task)
    result = await db.execute(query)
    return result.scalars().all()


@alru_cache(maxsize=128)                                                #декоратор для кеширования async_lru
async def get_task(db: AsyncSession, task_id: int):                    #Получение информации о задаче
    query = select(Task).filter_by(id = task_id)
    result = await db.execute(query)
    return result.scalars().first()


async def update_task(db: AsyncSession, task_id: int, task: TaskUpdate):    #Обновление задачи
    query = select(Task).filter_by(id = task_id)
    result = await db.execute(query)
    db_task = result.scalars().first()
    if db_task:
        for key, value in task.model_dump(exclude_unset=True).items():     #проходим по словарю, exclude_unset исключает неустановленные поля
            setattr(db_task, key, value)                                   #устанавливаем атрибуты объекта
        await db.commit()
        await db.refresh(db_task)
        task_to_schema.cache_clear()                                        #очистка кеша при обновлении
        get_tasks_user.cache_clear()
        get_tasks_all.cache_clear()
    return db_task


async def update_user(db: AsyncSession, user_id: int, user: schemas.UserUpdate):
    query = select(User).filter_by(id=user_id)
    result = await db.execute(query)
    db_user = result.scalars().first()
    if db_user:
        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(db_user, key, value)
        await db.commit()
        await db.refresh(db_user)
        user_to_schema.cache_clear()
        get_all_users.cache_clear()
        return db_user
    return None


async def delete_task(db: AsyncSession, task_id: int):                  #удаление задачи
    query = select(Task).filter_by(id = task_id)
    result = await db.execute(query)
    db_task = result.scalars().first()
    if db_task:
        await db.execute(delete(Task).where(Task.id == task_id))
        await db.commit()
        task_to_schema.cache_clear()                                    #очистка кеша при обновлении
        get_tasks_user.cache_clear()
        get_tasks_all.cache_clear()
        return {"message": "Задача удалена"}
    return {"message": "Задача не найдена"}


async def delete_user(db: AsyncSession, user_id: int):
    query = select(User).filter_by(id=user_id)
    result = await db.execute(query)
    db_user = result.scalars().first()
    if db_user:
        user_data = await user_to_schema(db, db_user)
        await db.execute(delete(User).filter_by(id=user_id))
        await db.commit()
        user_to_schema.cache_clear()
        get_all_users.cache_clear()
        return {"message": f"Пользователь {user_data} удален"}
    return {"message": "Пользователь не найден"}



@alru_cache(maxsize=128)                  #декоратор для кеширования async_lru
async def task_to_schema(db: AsyncSession, task: Task) -> schemas.Task:
    user = await db.execute(select(User).filter(User.id == task.user_id))  #преобразовываем задачу в схему для уменьшения повторов
    user = user.scalar_one()
    return schemas.Task(
        id=task.id,
        title=task.title,
        description=task.description,
        created_at=task.created_at,
        updated_at=task.updated_at,
        user_name=user.name,
        user_surname=user.surname
    )

