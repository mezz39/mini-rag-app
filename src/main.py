from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv(".env")
from routes import base, data, datadebug
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings

from stores.llm.LLMProviderFactory import LLMProviderFactory

app = FastAPI()

async def startup_db_client():
    settings = get_settings()
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)
    app.state.db_client = [settings.MONGODB_DATABASE]
    llm_provider_factory = LLMProviderFactory(settings)
    # Generation
    app.state.generation_client = llm_provider_factory.create(provider=settings.Generation_backend)
    if app.state.generation_client is None:
        raise RuntimeError("Embedding LLM provider could not be initialized")
    app.state.generation_client.set_generation_model(model_id=settings.GENERATION_MODEl_ID)

    # Embedding
    app.state.embedding_client = llm_provider_factory.create(provider=settings.Embedding_backend)

    if app.state.embedding_client is None:
        raise RuntimeError("Embedding LLM provider could not be initialized")

    app.state.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                                   embedding_size= settings.EMBEDDING_MODEL_SIZE
    )

    
async def shutdown_db_client():
    app.state.mongo_conn.close()
    

app.state.router.lifespan.on_startup.append(startup_db_client)
app.state.router.lifespan.on_shutdown.append(shutdown_db_client)



app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(datadebug.debug_router)
