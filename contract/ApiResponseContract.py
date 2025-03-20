from typing import Any

from groq import BaseModel
from pydantic import Field


class ApiResponseContract(BaseModel):
    code: str = Field(default="00", max_length=2, min_length=2)
    msg: str = Field(default="Success", max_length=15)
    data: dict | str | Any = None

    @classmethod
    async def success_response(cls, data: data or None = None):
        instance = cls()
        return {"code": instance.code, "msg": instance.msg, "data": data}

    @classmethod
    async def failure_response(cls, data: data or None = None):
        return {"code": "99", "msg": "Failed", "data": data}
