from dotenv import load_dotenv
from langchain.schema import SystemMessage
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_mongodb import MongoDBChatMessageHistory
from pydantic import EmailStr
from starlette.exceptions import HTTPException

from database.ChatHistoryManager import ChatHistoryManager
from database.MongoDB import MongoDB
from model.UserChatModel import UserChatModel, ChatTitleModel
from model.UserDbEntity import UserDbEntity
from service.UserOperations import apiResponse

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
    timeout=1,
    max_retries=1
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
        chat.add_message(HumanMessage(content=chat_input.message))
        messages = await chat.aget_messages()
        ai_response = llm.invoke(messages)
        chat.add_message(AIMessage(content=ai_response.content))
        self.user_client.update_one({"email": chat_input.email}, {"$set": {}})
        return {"session_id": chat_input.session_id, "response": ai_response.content}

    @staticmethod
    async def get_session_title(message: str):
        prompt = f"""create a summarized title of 10 words or less for this ai chat. 
                output only the the title, don't include a word of yourself like 'Here's a summarized title for this chat'. 
                Here's the message : {message}
                """
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
        messages = await chat_history.aget_messages() or []

        if len(messages) == 0:
            chat_history.add_message(SystemMessage(content=chat_model.ai_character))
            session_title = await self.get_session_title(chat_model.message)
            sessions.append({"session_id": chat_model.session_id, "title": session_title})
            await self.user_client.update_one({"email": chat_model.email}, {"$set": {"session_list": sessions}})
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

    async def update_chat_title(self, payload: ChatTitleModel):
        user_record = await self.user_client.find_one({"email": payload.email})
        if user_record is None:
            raise HTTPException(status_code=404, detail="Account does not exist")

        chat_history: list = user_record.get("session_list")
        if len(chat_history) == 0:
            return apiResponse.failure_response("No records to update")

        record_found = False
        for item in chat_history:
            if item["session_id"] == payload.session_id:
                item["title"] = payload.new_title
                record_found = True
                break
        if record_found:
            await self.user_client.update_one({"email": payload.email}, {"$set": {"session_list": chat_history}})
            return await apiResponse.success_response("Chat title updated")
        raise HTTPException(detail=f"record with session id {payload.session_id} does not exist", status_code=404)
