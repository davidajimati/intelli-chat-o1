from bson import ObjectId
from pydantic import Field, BaseModel, EmailStr, validator


class UserDbEntity(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id", )
    email: EmailStr
    username: str = Field(max_length=20, min_length=3)
    session_list: list[dict[str, str]] = Field(default_factory=list)

    @validator("email", pre=True)
    def normalize_email(cls, v):
        return v.strip().lower()

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class NewUser(BaseModel):
    username: str = Field(max_length=20, min_length=3)
    email: EmailStr

    @validator("email", pre=True)
    def normalize_email(cls, v):
        return v.strip().lower()
