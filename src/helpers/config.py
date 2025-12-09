from pydantic_settings import BaseSettings, SettingsConfigDict

class settings(BaseSettings):

    APP_NAME: str 
    APP_VERSION: str
    OPEN_API_KEY: str
    ALLOWED_FILE_TYPES: list[str]
    FILE_MAX_SIZE: int  # in MB

    class config:
        env_file = ".env"

def get_settings():
    return settings()


