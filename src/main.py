from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv(".env")
from routes import base, data, datadebug
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from helpers.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.state.mongodb_client = client
    app.state.db_client = client[settings.MONGODB_DATABASE]

    yield
    
    client.close()

app = FastAPI(lifespan=lifespan)
app.add_event_handler("startup", lifespan)


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(datadebug.debug_router)
