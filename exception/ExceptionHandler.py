from fastapi import HTTPException, FastAPI
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from service.UserOperations import apiResponse


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return await JSONResponse(apiResponse.failure_response(str(exc.detail)), status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        if exc.errors() is not None:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "responseCode": "95",
                    "responseMessage": "Invalid request",
                    "errors": [str(error["loc"][1]) + " " + str(error["msg"]) for error in exc.errors()]
                    # "errors": exc.errors()
                }
            )
        else:
            return exc
