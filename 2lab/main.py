from fastapi import FastAPI
from app.api.endpoints import router
from app.db.session import engine
from app.db.base import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)
