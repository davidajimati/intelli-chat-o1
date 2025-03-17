from typing import Any

from pydantic import Field


class ApiResponseContract:
    code: str = Field(default="00", max_length=2, min_length=2)
    msg: str = Field(default="Success", max_length=15)
    data: dict | str | Any = None

    @classmethod
    def create_success_response(cls, data: data or None):
        instance = cls()
        return {"code": instance.code, "msg": instance.msg, "data": data}

    @classmethod
    def create_failure_response(cls, data: data or None):
        return {"code": "99", "msg": "Failed", "data": data}
