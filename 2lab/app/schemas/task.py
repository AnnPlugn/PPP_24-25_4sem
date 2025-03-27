from pydantic import BaseModel


class TaskCreate(BaseModel):
    url: str
    max_depth: int
    format: str


class TaskStatus(BaseModel):
    status: str
    progress: int
    result: str | None

    class Config:
        from_attributes = True
