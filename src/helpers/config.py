from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str 
    APP_VERSION: str
    OPEN_API_KEY: str
    ALLOWED_FILE_TYPES: list[str]
    FILE_MAX_SIZE: int  # in MB
    FILE_DEFAULT_CHUNK_SIZE: int  # in bytes

    class Config:
        env_file = "../.env"

def get_settings():
    return Settings(APP_NAME="My App", APP_VERSION="1.0.0", 
                    OPEN_API_KEY="your_api_key",
                    ALLOWED_FILE_TYPES=["text/plain", "application/pdf"], 
                    FILE_MAX_SIZE=10, FILE_DEFAULT_CHUNK_SIZE=512000)
