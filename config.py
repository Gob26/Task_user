from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    class Config:
        env_file = ".env"

class Settings_Test(BaseSettings):    #для тестов переводим export TEST_ENV=true
    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASSWORD: str
    TEST_DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return f'postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASSWORD}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}'

    class Config:
        env_file = ".env"

def get_settings():
    if os.getenv('TEST_ENV') == 'true':
        return Settings_Test()
    return Settings()

settings = get_settings()

# Пример проверки подключения
db_url = settings.DATABASE_URL_asyncpg
print(db_url)
