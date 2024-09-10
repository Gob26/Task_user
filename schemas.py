from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    user_name: str
    user_surname: str
    created_at: datetime
    updated_at: datetime

    class Config:                   #для чтения данных из orm
        orm_mode = True


class UserBase(BaseModel):
    name: str
    surname: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        orm_mode = True