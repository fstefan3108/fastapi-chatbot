from pydantic import BaseModel, Field, EmailStr


class UserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr = Field(max_length=100)
    password: str

class UserResponse(BaseModel):
    id: int
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr = Field(max_length=100)

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str