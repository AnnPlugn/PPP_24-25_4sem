from fastapi import FastAPI
from app.api.endpoints import router
from app.db.session import engine
from app.db.base import Base

app = FastAPI()

# Создание таблиц при запуске
Base.metadata.create_all(bind=engine)

# Подключение маршрутов
app.include_router(router)
