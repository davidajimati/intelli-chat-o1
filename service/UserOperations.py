from pydantic import EmailStr
import uuid

from contract.ApiResponseContract import ApiResponseContract
from database.MongoDB import MongoDB
from model.UserDbEntity import NewUser
from model.UserDbEntity import UserDbEntity
from starlette.exceptions import HTTPException
from database.ChatHistoryManager import ChatHistoryManager
from dotenv import load_dotenv

load_dotenv()
apiResponse = ApiResponseContract()
dbHistory = ChatHistoryManager()


class UserOperations:
    def __init__(self):
        self.user_client = MongoDB().users_collection

    async def create_user(self, user: NewUser):
        existing_user = await self.user_client.find_one({
            "$or": [{"email": user.email},
                    {"username": user.username}]
        })
        if existing_user:
            raise HTTPException(status_code=409, detail="user already exists")
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
        user = await self.user_client.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=400, detail="user does not exist")
        sessions = list(user.get("session_id_list") or [])

        if len(sessions) > 0:
            for session in sessions:
                history = await dbHistory.history_instance(session)
                history.clear()
        self.user_client.delete_one({"email": email})
        return await apiResponse.success_response("account deleted successfully")

    @staticmethod
    async def create_new_session() -> dict:
        """
        create new Session ID for user
        :return apiResponse: json response containing the generate session ID
        """
        new_session_id = str(uuid.uuid4())
        return await apiResponse.success_response(new_session_id)

    async def get_chats_list(self, email: EmailStr) -> dict:
        user = await self.user_client.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="chats not found")
        sessions = user.get("session_list")
        if not isinstance(sessions, list):
            sessions = []
        return await apiResponse.success_response(sessions)

    @staticmethod
    async def get_chat_history(session_id: str) -> dict:
        db_history = await dbHistory.history_instance(session_id)
        if not db_history:
            raise HTTPException(status_code=404, detail="No chat history yet")
        history = await db_history.aget_messages()
        history_list = [{chat.type: chat.content} for chat in history]
        return await apiResponse.success_response(history_list)

    async def get_all_users(self):
        user_cursor = self.user_client.find()
        users = await user_cursor.to_list(length=None)
        return await apiResponse.success_response([{"username": x["username"], "email": x["email"]} for x in users])

    async def update_username(self, user_details: NewUser):
        user_record = await self.user_client.find_one({"email": user_details.email})
        if user_record is None:
            raise HTTPException(status_code=404, detail="Account does not exist")

        await self.user_client.update_one({"email": user_details.email}, {"$set": {"username": user_details.username}})
        return await apiResponse.success_response("username updated")
