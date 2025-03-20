from langchain_mongodb import MongoDBChatMessageHistory
from motor.motor_asyncio import AsyncIOMotorClient
import os


class MongoDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
        self.db = self.client["intelli_chat_o1"]
        self.users_collection = self.db["registered_users"]
