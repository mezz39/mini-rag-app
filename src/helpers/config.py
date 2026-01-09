from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
class Settings(BaseSettings):
    

    APP_NAME: str = "mini rag"
    APP_VERSION: str = "1.0.0"

    ALLOWED_FILE_TYPES: list[str] = ["text/plain", "application/pdf"]
    FILE_MAX_SIZE: int = 10  # in MB
    FILE_DEFAULT_CHUNK_SIZE: int = 512000  # in bytes

    MONGODB_URI: str = "mongodb://localhost:27007"
    MONGODB_DATABASE: str = "mydatabase"

    Generation_backend :str
    Embedding_backend :str

    OPENAI_API_KEY :str
    OPENAI_API_URL :str
    COHERE_API_KEY : str

    GENERATION_MODEl_ID : str  
    EMBEDDING_MODEL_ID : str
    EMBEDDING_MODEL_SIZE :int
    input_max_input_characters: Optional[int] = None
    default_generation_max_output: Optional[int] = None
    default_generation_temperature: Optional[float] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        arbitrary_types_allowed = True # 'ignore' is safer than 'allow' for config
    )  # allows unknown fields without errors

def get_settings():
    return Settings() # type: ignore
