from celery import Celery
from app.core.config import settings
from app.services.parser import parse_website_task

celery_app = Celery("tasks", broker=settings.REDIS_URL)


@celery_app.task(name="parse_website_task")
def parse_website_task_wrapper(task_id: int, url: str, max_depth: int, format: str):
    result = parse_website_task(task_id, url, max_depth, format)
    return result  # Возвращаем результат для Celery
