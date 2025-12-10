from fastapi import FastAPI, APIRouter, Depends
from helpers import get_settings, Settings
import os
base_router = APIRouter(prefix= "/api/v1",
            tags= ["api_v1"]
)

@base_router.get("/welcome")
async def welcome(app_settings: Settings= Depends(get_settings)):
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    allowed_file_types = app_settings.ALLOWED_FILE_TYPES
    
    return {"app_name": app_name,
            "app_version": app_version,
            "allowed_file_types": allowed_file_types}
