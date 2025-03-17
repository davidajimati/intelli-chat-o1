from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import EmailStr
from model import ChatHistoryModel
from model.UserChatModel import UserChatModel
from model.NewUser import NewUser
from service.DbOperations import DbOperations

load_dotenv()
app = FastAPI()
db_agent = DbOperations()


class Controller:
    @staticmethod
    @app.post("/create-new-user")
    async def create_new_user(user: NewUser):
        return db_agent.create_user(user)

    @staticmethod
    @app.post("/message")
    async def chat_ai(chat_input: UserChatModel) -> str:
        pass

    @staticmethod
    @app.post("/chats-list")
    async def get_previous_chats(email: EmailStr) -> list[str]:
        pass

    @staticmethod
    @app.get("/chat-history")
    async def get_chat_history(session_id: str) -> ChatHistoryModel:
        pass
