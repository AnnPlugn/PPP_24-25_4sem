from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate


def create_task(db: Session, task: TaskCreate):
    db_task = Task(url=task.url, max_depth=task.max_depth, format=task.format)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_by_id(db: Session, task_id: int):  # Исправлено: str -> int
    return db.query(Task).filter(Task.id == task_id).first()


def update_task(db: Session, task: Task, status: str, progress: int, result: str = None):
    task.status = status
    task.progress = progress
    task.result = result
    db.commit()
    db.refresh(task)
    return task
