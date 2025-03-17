from pydantic import BaseModel, EmailStr


class UserChatModel(BaseModel):
    session_id: str
    message: str
