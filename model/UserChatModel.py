import uuid

from pydantic import BaseModel, Field, EmailStr, validator

from service.UserOperations import UserOperations

user_operations = UserOperations()


class UserChatModel(BaseModel):
    session_id: str | None = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    message: str
    ai_character: str = Field(default="You're a funny, helpful and intelligent assistant. Your name is David")

    @validator("email", pre=True)
    def normalize_email(cls, v):
        return v.strip().lower()


class ChatTitleModel(BaseModel):
    session_id: str
    email: EmailStr
    new_title: str

    @validator("email", pre=True)
    def normalize_email(cls, v):
        return v.strip().lower()
