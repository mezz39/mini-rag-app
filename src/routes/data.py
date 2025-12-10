from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from controllers import DataController
from controllers import ProjectController
from helpers import get_settings, Settings
from models.enums.ResponseEnums import ResponseSignal
import aiofiles
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
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content= {"message": is_valid})

    project_dir_path = ProjectController().get_project_path(project_id)
    file_path = os.path.join(
        project_dir_path, 
        file.filename or "default_filename"
        )
    file_path = DataController().generate_unique_filename(
        original_filename= file.filename or "default_filename",
        project_id= project_id
    )
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    await file.seek(0)
    
    async with aiofiles.open(file_path,'wb') as f:
        while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
            
            await f.write(chunk)


    return JSONResponse(
        content= {
            "signal": "File_Upload_Successful",
            }
    )