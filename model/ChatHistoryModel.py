from pydantic import BaseModel
from langchain_mongodb import MongoDBChatMessageHistory


class ChatHistoryModel(BaseModel):
    session_id: str
    chat_history: MongoDBChatMessageHistory
