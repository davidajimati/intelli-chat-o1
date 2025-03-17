from bson import ObjectId
from pydantic import BaseModel, Field
from langchain_mongodb import MongoDBChatMessageHistory


class ChatHistoryModel(BaseModel):
    id: ObjectId() = Field(default_factory=lambda: ObjectId(), alias="_id")
    session_id: str
    chat_history: MongoDBChatMessageHistory | None = None
