from pydantic import EmailStr, UUID1

from contract.ApiResponseContract import ApiResponseContract
from database.MongoDB import MongoDB
from model.UserDbEntity import NewUser
from model.UserDbEntity import UserDbEntity
from starlette.exceptions import HTTPException
from langchain_mongodb import MongoDBChatMessageHistory

api_response = ApiResponseContract()


class UserOperations:
    def __init__(self):
        self.user_client = MongoDB().users_collection
        self.user_chat_history = MongoDB().chat_history_collection

    async def create_user(self, user: NewUser):
        user_entity = UserDbEntity(username=user.username, email=user.email)
        entity = self.user_client.insert_one(user_entity.model_dump(by_alias=True))
        if not entity:
            raise HTTPException(status_code=400, detail="user could not be created")
        return await api_response.success_response("user created")

    async def delete_user(self, email: EmailStr) -> dict:
        """
        Delete a user from record
        :param email:
        :return dict:
        """
        user = self.user_client.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=400, detail="user does not exist")
        sessions = list(user.get("session_id_list") or None)

        if len(sessions) > 0:
            self.user_chat_history.delete_many({"session_id": {"$in": sessions}})
        return await api_response.success_response("account deleted successfully")

    @staticmethod
    async def create_new_session() -> dict:
        """
        create new Session ID for user
        :return api_response: json response containing the generate session ID
        """
        new_session_id = UUID1()
        return await api_response.success_response(new_session_id)

    async def add_new_session(self, session_id: UUID1, title: str, email: EmailStr) -> bool:
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

        record = {"session_id": session_id, "title": title}
        sessions = list(user.get("session_list") or [])
        sessions.append(record)

        user = self.user_client.update_one({
            {"email": email},
            {"session_list": sessions}
        })
        if not user: return False
        return True

    async def get_chats_list(self, email: EmailStr) -> dict:
        user = self.user_client.find_one({"email": email})
        history = list[user.get("session_list") or []]
        return await api_response.success_response(history)

    async def get_chat_history(self, session_id: str) -> dict:
        chat_history = await self.user_chat_history.find_one({"session_id": session_id})
        if not chat_history: raise HTTPException(status_code=400, detail="session does not exist")
        return await api_response.success_response(chat_history)

    async def message_history(self, session_id: str):
        raw_history = await self.user_chat_history.find_one({"session_id": session_id})
        chat_history = MongoDBChatMessageHistory(raw_history, session_id)
        return chat_history
