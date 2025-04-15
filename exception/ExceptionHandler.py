from http.client import HTTPException

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from service.UserOperations import apiResponse

app = FastAPI()
apiResponse()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return await JSONResponse(apiResponse.success_response(str(exc.detail)), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request, exc):
    return JSONResponse(str(exc), status_code=400)
