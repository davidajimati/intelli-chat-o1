from http.client import HTTPException

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from service.UserOperations import apiResponse

app = FastAPI()
apiResponse()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return await JSONResponse(apiResponse.success_response(str(exc.detail)), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )
