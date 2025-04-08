import os
from langchain_mongodb import MongoDBChatMessageHistory
from pymongo import MongoClient


class ChatHistoryManager:
    @staticmethod
    async def history_instance(session_id: str) -> MongoDBChatMessageHistory:
        return MongoDBChatMessageHistory(
            collection_name="chat_history",
            session_id=str(session_id),
            connection_string=os.getenv("MONGODB_URL"),
            database_name="intelli_chat_o1"
        )
