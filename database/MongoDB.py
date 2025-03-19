from langchain_mongodb import MongoDBChatMessageHistory
from motor.motor_asyncio import AsyncIOMotorClient
import os


class MongoDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
        self.db = self.client["intelli_chat_o1"]
        self.users_collection = self.db["registered_users"]
        self.chat_history_collection = self.db["users_chat_list"]

    async def create_indexes(self):
        await self.users_collection.create_indexe("email", unique=True)
        await self.users_collection.create_indexe("email", unique=True)

    async def close_connection(self):
        self.client.close()
