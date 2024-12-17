from contextlib import asynccontextmanager
import json
from fastapi import FastAPI
from fastapi_cors import CORS
from database import init_db

from models import Car, CurrentUser, User
from routers import users as user_router
from routers import cars as car_router


# print(json.dumps(Car.model_json_schema(), indent=2))  # (2)!
# print(json.dumps(User.model_json_schema(), indent=2))
# print(json.dumps(CurrentUser.model_json_schema(), indent=2))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
CORS(app)


app.include_router(user_router.router, prefix="/users", tags=["Users"])
app.include_router(car_router.router, prefix="/cars", tags=["Cars"])

@app.get("/", tags=["Root"])
async def read_root() -> dict:
    return {"message": "Welcome to your beanie powered app!"}
