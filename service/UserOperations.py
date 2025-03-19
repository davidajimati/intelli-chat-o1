from pydantic import EmailStr, UUID1

from contract.ApiResponseContract import ApiResponseContract
from database.MongoDB import MongoDB
from model.UserDbEntity import NewUser
from model.UserDbEntity import UserDbEntity
from starlette.exceptions import HTTPException
from database.ChatHistoryManager import ChatHistoryManager

apiResponse = ApiResponseContract()
dbHistory = ChatHistoryManager()


class UserOperations:
    def __init__(self):
        self.user_client = MongoDB().users_collection

    async def create_user(self, user: NewUser):
        user_entity = UserDbEntity(username=user.username, email=user.email)
        entity = self.user_client.insert_one(user_entity.model_dump(by_alias=True))
        if not entity:
            raise HTTPException(status_code=400, detail="user could not be created")
        return await apiResponse.success_response("user created")

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
            for session in sessions:
                history = await dbHistory.history_instance(session)
                history.clear()
        return await apiResponse.success_response("account deleted successfully")

    @staticmethod
    async def create_new_session() -> dict:
        """
        create new Session ID for user
        :return apiResponse: json response containing the generate session ID
        """
        new_session_id = UUID1()
        return await apiResponse.success_response(new_session_id)

    async def get_chats_list(self, email: EmailStr) -> dict:
        user = self.user_client.find_one({"email": email})
        history = list[user.get("session_list") or []]
        return await apiResponse.success_response(history)

    @staticmethod
    async def get_chat_history(session_id: str) -> dict:
        history = await dbHistory.history_instance(session_id)
        return await apiResponse.success_response(history)
