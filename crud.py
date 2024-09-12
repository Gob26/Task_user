from dns.e164 import query
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
    return db_task


async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_tasks_user(db: AsyncSession, user_id: int):              # Получение списка задач для пользователя
    query = select(Task).filter(Task.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()                                      #scalars для простых типов данных


async def get_tasks_all(db: AsyncSession):                             #Получение всех задач с указанием пользователей
    query = select(Task)
    result = await db.execute(query)
    return result.scalars().all()


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
        await db.refresh(db_task)                                          #обновит чтобы отображал актуальное состояние бд
    return db_task


async def delete_task(db: AsyncSession, task_id: int):                  # Удаление задачи
    query = select(Task).filter(Task.id == task_id)
    result = await db.execute(query)
    db_task = result.scalars().first()
    if db_task:
        # Удаление записи
        await db.execute(delete(Task).where(Task.id == task_id))
        await db.commit()
        return {"message": "Задача удалена"}
    return {"message": "Задача не найдена"}


async def task_to_schema(db: AsyncSession, task: Task) -> schemas.Task:
    user = await db.execute(select(User).filter(User.id == task.user_id))  #преобразовываем задачу в схему
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

