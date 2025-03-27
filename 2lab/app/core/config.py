from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    REDIS_URL: str = "redis://localhost:6379/0"  # Значение по умолчанию

    class Config:
        env_file = ".env"


settings = Settings()
