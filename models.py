from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from datetime import datetime
from typing import Annotated


intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)] #сократили, авто уник значение


class User(Base):
    __tablename__ = "users"
    id: Mapped[intpk]
    name: Mapped[str]
    surname: Mapped[str]

    tasks: Mapped[list["Task"]] = relationship("Task",
                                               back_populates="owner",
                                               cascade='all, delete-orphan') #каскадное удаление

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[intpk]
    title: Mapped[str]
    description: Mapped[str|None]
    created_at: Mapped[datetime] = mapped_column(server_default=text('TIMEZONE(\'utc\', NOW())'))  # тестировать
    updated_at: Mapped[datetime] = mapped_column(server_default=text('TIMEZONE(\'utc\', NOW())'),
    onupdate=datetime.utcnow)                                                                      # заменить
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    owner: Mapped["User"] = relationship("User", back_populates="tasks")