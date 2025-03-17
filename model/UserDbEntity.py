from pydantic import Field, BaseModel, EmailStr
from langchain_mongodb import MongoDBChatMessageHistory


class UserDbEntity(BaseModel):
    username: str = Field(max_length=20, min_length=3)
    email: EmailStr
    chat_history: MongoDBChatMessageHistory | None = None
    session_id_list: list[str] | None = None
