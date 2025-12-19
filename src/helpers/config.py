from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore" # 'ignore' is safer than 'allow' for config
    )  # allows unknown fields without errors

    APP_NAME: str = "mini rag"
    APP_VERSION: str = "1.0.0"
    OPEN_API_KEY: str = "your_api_key"

    ALLOWED_FILE_TYPES: list[str] = ["text/plain", "application/pdf"]
    FILE_MAX_SIZE: int = 10  # in MB
    FILE_DEFAULT_CHUNK_SIZE: int = 512000  # in bytes

    MONGODB_URI: str = "mongodb://localhost:27007"
    MONGODB_DATABASE: str = "mydatabase"
    

def get_settings():
    # Construct Settings without explicit overrides so environment variables
    # and the .env file are respected. If necessary, callers may override
    # values via environment variables.
    return Settings()
