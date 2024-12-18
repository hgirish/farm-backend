import json
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException
from fastapi.responses import JSONResponse

from authentication import AuthHandler
from background import delayed_task
from models import CurrentUser, LoginUser, RegisterUser, User

auth_handler = AuthHandler()
router = APIRouter()


@router.post(
    "/register",
    response_description="Register user",
    response_model=CurrentUser
)
async def register(
    newUser: RegisterUser = Body(...),
    response_model=User
):
    newUser.password = auth_handler.get_password_hash(newUser.password)

    query = {
        "$or": [{"username": newUser.username},
                {"email": newUser.email}]
    }
    existing_User = await User.find_one(query)

    if existing_User is not None:
        raise HTTPException(status_code=409, detail=f"{newUser.username} or {newUser.email} already exists")
    user = await User(**newUser.model_dump()).save()
    return user


@router.post("/login", response_description="Login user and return token")
async def login(background_tasks: BackgroundTasks,
                loginUser: LoginUser = Body(...)) -> str:
    user = await User.find_one(User.username == loginUser.username)

    if user and auth_handler.verify_password(loginUser.password, user.password):
        token = auth_handler.encode_token(str(user.id), user.username)
        background_tasks.add_task(delayed_task, username=user.username)
        response = JSONResponse(content={
            "token": token,
            "username": user.username
        })
        return response
    else:
        raise HTTPException(
            status_code=401, detail="Invalid username or password")


@router.get("/me", response_description="Logged in user data", response_model=CurrentUser)
async def me(user_data=Depends(auth_handler.auth_wrapper)):
    json_user_data = json.loads(user_data)
    print(json_user_data)
    current_user = await User.get(json_user_data["user_id"])
    return current_user
