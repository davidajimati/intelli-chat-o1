from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import EmailStr

from model.UserChatModel import UserChatModel
from model.UserDbEntity import NewUser
from service.UserOperations import UserOperations, apiResponse
from service.AiOperations import AiOperations

load_dotenv()
app = FastAPI()
userOperations = UserOperations()
aiOperations = AiOperations()


@app.post("/create-new-user")
async def create_new_user(user: NewUser) -> dict:
    """
    create a new user
    :param user:
    :return dict[str]:
    """
    return await userOperations.create_user(user)


@app.delete("/delete-user/{email}")
async def create_new_user(email: EmailStr) -> dict:
    """
    delete all user records. this action is irreversible
    :param email:
    :return dict[str]:
    """
    return await userOperations.delete_user(email)


@app.get("/new-session")
async def new_session() -> dict:
    """
    create a new session ID for a new chat
    :return:
    """
    return await userOperations.create_new_session()


@app.get("/chats-list/{email}")
async def get_chat_list(email: EmailStr) -> dict:
    """
    fetch all list of past chats with the LLM
    :param email:
    :return dict:
    """
    return await userOperations.get_chats_list(email)


@app.get("/chat-history/{session_id}")
async def get_chat_history(session_id: str) -> dict:
    """
    get chat history for current session
    :param session_id:
    :return dict:
    """
    return await userOperations.get_chat_history(session_id)


@app.post("/chat_input")
async def chat_ai(message: UserChatModel) -> dict:
    """
    chat with the LLM
    :param message: user input. contains sessionId and
    :return dict[str]:
    """
    ai_response =  await aiOperations.chat_ai(message)
    return apiResponse.success_response({"message": ai_response})
