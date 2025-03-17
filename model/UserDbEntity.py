from bson import ObjectId
from pydantic import Field, BaseModel, EmailStr
from langchain_mongodb import MongoDBChatMessageHistory
from pydantic.v1 import UUID1


class UserDbEntity(BaseModel):
    id: ObjectId() = Field(default_factory=lambda: ObjectId(), alias="_id", )
    email: EmailStr
    username: str = Field(max_length=20, min_length=3)
    session_list: list[dict[UUID1, str]] | None = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class NewUser(BaseModel):
    username: str = Field(max_length=20, min_length=3)
    email: EmailStr
