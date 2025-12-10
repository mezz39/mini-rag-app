from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from controllers import DataController
from helpers import get_settings, Settings
import os
data_router = APIRouter(prefix= "/api/v1/data",
            tags= ["api_v1", "data"])
@data_router.get("/test")
async def test():
    return {"status": "ok"}

@data_router.post("/upload/{project_id}")
async def upload_data(project_id:str, file: UploadFile, app_settings: Settings= Depends(get_settings)):
    
    
    # validate the file type and size
    is_valid = await DataController().validate_uploaded_file(file)
    
    if not is_valid:
        return JSONResponse(status_code= status.HTTP_400_BAD_REQUEST,
                            content= {"message": is_valid})

