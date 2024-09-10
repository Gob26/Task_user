from sqlalchemy import select
from schemas import TaskUpdate, TaskCreate
from models import Task
from sqlalchemy.ext.asyncio import AsyncSession


async def create_task(db: AsyncSession, task: TaskCreate, user_id: int):                 #Создание задачи
    db_task = Task(**task.model_dump(), user_id=user_id)                #model_dump т к dict больше не рекомендуется к использованию и будет удален в будущих версиях
    db.add(db_task)
    await db.refresh(db_task)
    await db.commit()
    return db_task


async def get_tasks_user(db: AsyncSession, user_id: int):              #Получение списка задач для пользователя
    query = select(Task).filter_by(id = user_id)
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


async def delete_task(db: AsyncSession, task_id: int):                  #Удаление задачи
    query = select(Task).filter_by(id = task_id)
    result = await db.execute(query)
    db_task =result.scalars().first()
    if db_task:
        await db.delete(db_task)
        await db.commit()
        return {"message": "Задача удалена"}
    return {"message": "Задача не найдена"}


