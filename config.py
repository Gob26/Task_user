from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    def DATABASE_URL_asyncpg(self) -> str:
        # Формируем строку подключения для asyncpg
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    class Config:
        env_file = ".env"

# проверка подключения
#settings = Settings()
#db_url = settings.DATABASE_URL_asyncpg()
#print(db_url)