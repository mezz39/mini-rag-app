from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv(".env")
from routes import base, data, datadebug
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from helpers.config import get_settings
from models.db_schemas import DataChunk, Project
import logging

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.state.mongodb_client = client
    app.state.db_client = client[settings.MONGODB_DATABASE]

    # Create indexes on startup
    try:
        db = app.state.db_client
        
        # Create indexes for data_chunks collection
        chunks_collection = db["data_chunks"]
        for index_spec in DataChunk.get_indexes():
            await chunks_collection.create_index(index_spec["key"], name=index_spec.get("name"), unique=index_spec.get("unique", False))
            logger.info(f"Created index on data_chunks: {index_spec['name']}")
        
        # Create indexes for projects collection
        projects_collection = db["projects"]
        for index_spec in Project.get_indexes():
            await projects_collection.create_index(index_spec["key"], name=index_spec.get("name"), unique=index_spec.get("unique", False))
            logger.info(f"Created index on projects: {index_spec['name']}")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

    yield
    
    client.close()

app = FastAPI(lifespan=lifespan)
app.add_event_handler("startup", lifespan)


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(datadebug.debug_router)
