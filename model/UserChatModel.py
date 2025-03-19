from pydantic import BaseModel, Field, UUID1
from service.UserOperations import UserOperations

user_operations = UserOperations()


class UserChatModel(BaseModel):
    session_id: str | None = Field(default_factory=lambda: str(UUID1()))
    message: str
    ai_character: str = Field(default="You're a helpful assistant")
