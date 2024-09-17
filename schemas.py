from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):          #для возможного расширения
    pass


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None


class Task(TaskBase):
    id: int
    user_name: str
    user_surname: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    surname: str


class UserUpdate(UserBase):
    name: Optional[str] = None
    surname: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        from_attributes = True

