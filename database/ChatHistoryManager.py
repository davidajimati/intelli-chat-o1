import os
from langchain_mongodb import MongoDBChatMessageHistory


class ChatHistoryManager:
    def __init__(self):
        self.connection_string = (os.getenv("MONGODB_URL_FOR_HISTORY"))
        self.collection = "chat_history"

    async def history_instance(self, session_id: str):
        return MongoDBChatMessageHistory(
            session_id=str(session_id),
            connection_string=self.connection_string,
            collection_name=self.collection
        )
