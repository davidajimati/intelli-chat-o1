from langchain_mongodb import MongoDBChatMessageHistory
from pydantic import EmailStr
from starlette.exceptions import HTTPException

from database.MongoDB import MongoDB
from model.UserChatModel import UserChatModel
from langchain_groq import ChatGroq
from database.ChatHistoryManager import ChatHistoryManager
from langchain.schema import SystemMessage, HumanMessage

chatHistoryDB = ChatHistoryManager()

llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=1,
    timeout=3,
    max_retries=2
)


class AiOperations:
    def __init__(self):
        self.user_client = MongoDB().users_collection

    async def chat_ai(self, chat_input: UserChatModel) -> str:
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
        return ai_response.content

    @staticmethod
    async def instantiate_chat(chat_model: UserChatModel) -> MongoDBChatMessageHistory:

        chat_history = await chatHistoryDB.history_instance(chat_model.session_id)
        messages = await chat_history.aget_messages()
        if messages is None:
            chat_history.add_message(SystemMessage(content=chat_model.ai_character))
        return chat_history

    async def add_new_session(self, session_id: str, title: str, email: EmailStr) -> bool:
        """
        add new session ID to user records
        :param title: chat title
        :param session_id: current user session ID
        :param email: user email
        :return bool: True if operation is successful, else, False
        """

        user = self.user_client.find_one({"email": email})
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
