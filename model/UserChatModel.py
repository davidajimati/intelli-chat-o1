from pydantic import BaseModel, Field, EmailStr
import uuid
from service.UserOperations import UserOperations

user_operations = UserOperations()


class UserChatModel(BaseModel):
    session_id: str | None = Field(default_factory=lambda: str(uuid.uuid4()))
    # email: EmailStr
    message: str
    ai_character: str = Field(default="You're a helpful assistant")
