from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str = Field(min_length=3, max_length=100)
    password: str

