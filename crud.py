from async_lru import alru_cache     #кеширование
from sqlalchemy import select, delete
import schemas
from schemas import TaskUpdate, TaskCreate, UserCreate
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
    return db_user
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
        # Очистка кэша после создания задачи
        task_to_schema.cache_clear()                                        #очистка кеша при обновлении
        get_tasks_user.cache_clear()
        get_tasks_all.cache_clear()
        #обновит чтобы отображал актуальное состояние бд
    return db_task


async def delete_task(db: AsyncSession, task_id: int):                  # Удаление задачи
    query = select(Task).filter(Task.id == task_id)
    result = await db.execute(query)
    db_task = result.scalars().first()
    if db_task:
        # Удаление записи
        await db.execute(delete(Task).where(Task.id == task_id))
        await db.commit()
        # Очистка кэша после создания задачи
        task_to_schema.cache_clear()                                    #очистка кеша при обновлении
        get_tasks_user.cache_clear()
        get_tasks_all.cache_clear()
        return {"message": "Задача удалена"}
    return {"message": "Задача не найдена"}

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

