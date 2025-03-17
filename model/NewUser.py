from pydantic import Field, EmailStr

from pydantic import BaseModel


class NewUser(BaseModel):
    username: str = Field(max_length=20, min_length=3)
    email: EmailStr
