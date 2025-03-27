from sqlalchemy import Column, Integer, String
from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    max_depth = Column(Integer, nullable=False)
    format = Column(String, nullable=False)
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)
    result = Column(String, nullable=True)
