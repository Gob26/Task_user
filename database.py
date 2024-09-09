from databases import Database    #асинхронное подключение к базе данных
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from config import settings


database = Database(settings.DATABASE_URL)
metadata = MetaData()
Base = declarative_base(metadata=metadata)


