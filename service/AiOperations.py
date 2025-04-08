from langchain_mongodb import MongoDBChatMessageHistory
from pydantic import EmailStr
from starlette.exceptions import HTTPException

from database.MongoDB import MongoDB
from model.UserChatModel import UserChatModel
from langchain_groq import ChatGroq
from database.ChatHistoryManager import ChatHistoryManager
from langchain.schema import SystemMessage
from dotenv import load_dotenv

from model.UserDbEntity import UserDbEntity

load_dotenv()
chatHistoryDB = ChatHistoryManager()

llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=1,
    timeout=5,
    max_retries=2
)

summaryLlm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    timeout=2,
    max_retries=2
)


class AiOperations:
    def __init__(self):
        self.user_client = MongoDB().users_collection

    async def chat_ai(self, chat_input: UserChatModel) -> dict:
        """
        send message to the llm
        :param chat_input:
        :return str:
        """
        chat: MongoDBChatMessageHistory = await self.instantiate_chat(chat_input)
        chat.add_user_message(chat_input.message)
        messages = await chat.aget_messages()
        ai_response = llm.invoke(messages)
        chat.add_ai_message(ai_response.content)
        return {"session_id": chat_input.session_id, "response": ai_response.content}

    @staticmethod
    async def get_session_title(message: str):
        prompt = f"create a summarized title for this chat: {message}"
        ai_response = summaryLlm.invoke(prompt).content
        return ai_response

    async def instantiate_chat(self, chat_model: UserChatModel) -> MongoDBChatMessageHistory:
        """
        checks if session_id exists; creates a new record if not
        :param chat_model:
        :return MongoDBChatMessageHistory:
        """
        user: UserDbEntity = await self.user_client.find_one({"email": str(chat_model.email)})
        if not user:
            raise HTTPException(status_code=404, detail="Please create an account to continue")
        sessions: [] = user.get("session_list") or []

        chat_history = await chatHistoryDB.history_instance(chat_model.session_id)
        messages = await chat_history.aget_messages()

        if messages is None:
            chat_history.add_message(SystemMessage(content=chat_model.ai_character))
            session_title = await self.get_session_title(chat_model.message)
            session_info = {"session_id": chat_model.session_id, "title": session_title}
            sessions.append(session_info)

            result = await self.user_client.update_one(
                {"email": str(chat_model.email)},
                {"$set": {"session_list": sessions}}
            )
            # await self.user_client.update_one({"email": chat_model.email}, {"$set": {"session_list": sessions}})

        return chat_history

    async def add_new_session(self, session_id: str, title: str, email: EmailStr) -> bool:
        """
        add new session ID to user records
        :param title: chat title
        :param session_id: current user session ID
        :param email: user email
        :return bool: True if operation is successful, else, False
        """

        user = await self.user_client.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=400, detail="user does not exist")

        sessions = list(user.get("session_list") or [])
        record = {"session_id": session_id, "title": title}
        sessions.append(record)

        user = self.user_client.update_one({
            {"email": email},
            {"session_list": sessions}
        })
        if not user: return False
        return True
