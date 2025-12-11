from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "allow"  # allows unknown fields without errors

    APP_NAME: str 
    APP_VERSION: str
    OPEN_API_KEY: str

    ALLOWED_FILE_TYPES: list[str]
    FILE_MAX_SIZE: int  # in MB
    FILE_DEFAULT_CHUNK_SIZE: int  # in bytes

    MONGODB_URI: str
    MONGODB_DATABASE: str
    

def get_settings():
    return Settings(APP_NAME="My App", 
                    APP_VERSION="1.0.0", 
                    OPEN_API_KEY="your_api_key",
                    ALLOWED_FILE_TYPES=["text/plain", "application/pdf"], 
                    FILE_MAX_SIZE=10,
                    FILE_DEFAULT_CHUNK_SIZE=512000,
                    MONGODB_URI="mongodb://localhost:27007",
                    MONGODB_DATABASE="mydatabase")
