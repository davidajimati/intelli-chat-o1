from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import EmailStr

from database.MongoDB import MongoDB
from exception.ExceptionHandler import register_exception_handlers
from model.UserChatModel import UserChatModel, ChatTitleModel
from model.UserDbEntity import NewUser
from service.AiOperations import AiOperations
from service.UserOperations import UserOperations, apiResponse

load_dotenv()

app = FastAPI()
db = MongoDB()
userOperations = UserOperations()
aiOperations = AiOperations()
register_exception_handlers(app)


@app.on_event("startup")
async def start_up_event():
    db.users_collection.create_index("email", unique=True)


@app.post("/create-new-user")
async def create_new_user(user: NewUser):
    """
    create a new user
    :param user:
    :return dict[str]:
    """
    return await userOperations.create_user(user)


@app.get("/get-all-users")
async def get_all_users():
    """
    get the list of registered users
    :return: list[str]
    """
    return await userOperations.get_all_users()


@app.put("/update-username")
async def update_username(user_details: NewUser):
    """
    update username of an existing user
    :param user_details:
    :return:
    """
    return await userOperations.update_username(user_details)


@app.delete("/delete-user/{email}")
async def delete_user(email: EmailStr):
    """
    delete all user records. this action is irreversible
    :param email:
    :return dict[str]:
    """
    return await userOperations.delete_user(email)


@app.get("/new-session")
async def new_session():
    """
    create a new session ID for a new chat
    :return:
    """
    return await userOperations.create_new_session()


@app.get("/chats-list/{email}")
async def get_chat_list(email: EmailStr):
    """
    fetch all list of past chats with the LLM
    :param email:
    :return dict:
    """
    return await userOperations.get_chats_list(email)


@app.get("/chat-history/{session_id}")
async def get_chat_history(session_id: str):
    """
    get chat history for current session
    :param session_id:
    :return dict:
    """
    return await userOperations.get_chat_history(session_id)


@app.put("/chat/update-title")
async def update_chat_title(payload: ChatTitleModel):
    """
    update the title of a chat with the model.
    :return: dict
    """
    return await aiOperations.update_chat_title(payload)


@app.post("/chat_input")
async def chat_ai(message: UserChatModel):
    """
    chat with the LLM
    :param message: user input. contains sessionId and
    :return dict[str]:
    """
    ai_response = await aiOperations.chat_ai(message)
    return await apiResponse.success_response({"message": ai_response})
