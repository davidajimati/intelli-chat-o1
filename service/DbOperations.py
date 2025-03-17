from pydantic import EmailStr

from contract.ApiResponseContract import ApiResponseContract
from database.MongoDB import MongoDB
from model.NewUser import NewUser
from model.UserDbEntity import UserDbEntity
from starlette.exceptions import HTTPException


class DbOperations:
    def __init__(self):
        self.user_client = MongoDB().users_collection
        self.user_chat_list = MongoDB().chat_history_collection

    def create_user(self, user: NewUser):
        user_entity = UserDbEntity(username=user.username, email=user.email, chat_history=None, session_id_list=[])
        entity = self.user_client.insert_one(user_entity)
        if not entity:
            raise HTTPException(status_code=400, detail="user could not be created")
        return ApiResponseContract.create_success_response("user created")

    def get_past_chat_list(self, email: EmailStr):
        pass

