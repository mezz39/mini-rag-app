from fastapi import FastAPI, APIRouter, Depends, UploadFile
from controllers import DataController
from helpers import get_settings, settings
import os
data_router = APIRouter(prefix= "/api/v1/data",
            tags= ["api_v1", "data"])

@data_router.post("/upload/{project_id}")
async def upload_data(project_id:str, file: UploadFile, app_settings: settings= Depends(get_settings)):
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    allowed_file_types = app_settings.ALLOWED_FILE_TYPES
    file_max_size = app_settings.FILE_MAX_SIZE
    
    # validate the file type and size
    is_valid = await DataController().validate_uploaded_file(file)
    if is_valid:
        return {"message": f"File '{file.filename}' uploaded successfully to project '{project_id}' in {app_name} v{app_version}."}


