from bson import ObjectId
from pydantic import Field, BaseModel, EmailStr



class UserDbEntity(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id", )
    email: EmailStr
    username: str = Field(max_length=20, min_length=3)
    session_list: list[dict[str, str]] = Field(default_factory=list)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class NewUser(BaseModel):
    username: str = Field(max_length=20, min_length=3)
    email: EmailStr
