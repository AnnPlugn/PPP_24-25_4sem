from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.task import TaskCreate, TaskStatus
from app.cruds.task import create_task, get_task_by_id
from app.db.session import get_db
from app.core.config import settings
from celery import Celery

router = APIRouter()

celery_app = Celery("tasks", broker=settings.REDIS_URL)


@router.get("/")
def read_root():
    return {"message": "Welcome to the Website Parser API. Use /parse_website to start parsing."}


@router.post("/parse_website", response_model=dict)
def parse_website(task: TaskCreate = None, db: Session = Depends(get_db)):
    if task is None or not task.url:
        task = TaskCreate(url="https://koroteev.site/?ysclid=m8rglns8hu760200624", max_depth=3, format="graphml")
    db_task = create_task(db, task)
    celery_app.send_task("parse_website_task", args=[db_task.id, task.url, task.max_depth, task.format])
    return {"task_id": db_task.id}


@router.get("/parse_status/{task_id}", response_model=TaskStatus)
def parse_status(task_id: int, db: Session = Depends(get_db)):
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": db_task.status, "progress": db_task.progress, "result": db_task.result}


@router.get("/parse_website", response_model=dict)
def parse_website_get(db: Session = Depends(get_db)):
    task = TaskCreate(url="https://koroteev.site/?ysclid=m8rglns8hu760200624", max_depth=3, format="graphml")
    db_task = create_task(db, task)
    celery_app.send_task("parse_website_task", args=[db_task.id, task.url, task.max_depth, task.format])
    return {"task_id": db_task.id}
