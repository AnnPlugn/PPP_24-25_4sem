from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    token: str

    class Config:
        from_attributes = True
