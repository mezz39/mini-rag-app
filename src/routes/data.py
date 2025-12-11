from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from controllers import DataController
from controllers import ProjectController
from controllers import ProcessController
from helpers import get_settings, Settings
from models.enums.ResponseEnums import ResponseSignal
import aiofiles
import os
import logging
from .schemas.data import ProcessRequest


logger = logging.getLogger("uvicorn.error")
data_router = APIRouter(prefix= "/api/v1/data",
            tags= ["api_v1", "data"])
@data_router.get("/test")
async def test():
    return {"status": "ok"}

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):

    # validate the file type and size
    is_valid = await DataController().validate_uploaded_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": is_valid}
        )

    # generate unique filename
    file_path, file_id = DataController().generate_unique_filename(
        original_filename=file.filename or "default_filename",
        project_id=project_id
    )

    # ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # reset file pointer
    await file.seek(0)

    # write the file to disk
    try:
        import aiofiles
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Error while uploading file: {e}"}
        )

    return JSONResponse(
        content={
            "signal": "File_Upload_Successful",
            "file_id": file_id,
            "file_path": file_path
        }
    )
@data_router.get("/debug-process/{project_id}/{file_id}")
async def debug_process(project_id: str, file_id: str):
    process = ProcessController(project_id)

    # 1️⃣ Get loader
    loader = process.get_file_loader(file_id)
    print("LOADER:", loader)

    # 2️⃣ Get file path
    file_path = process.get_file_path(file_id)
    print("FILE PATH:", file_path)
    file_extension = process.get_file_extension(file_id)
    print("FILE EXTENSION:", file_extension)
    # 3️⃣ Load file content
    file_content = process.get_file_content(file_id)
    print("FILE CONTENT RAW:", file_content)

    return {
        "loader": str(loader),
        "file_path": file_path,
        "file_extension": file_extension,
        "file_content_preview": file_content[:200] if file_content else None,
        "is_file_content_none": file_content is None
    }
@data_router.post("/process/{project_id}")
async def process_endpoint(project_id:str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    # normalize optional values from the request to plain ints
    process_controller = ProcessController(project_id=project_id)

    file_ext = process_controller.get_file_extension(
        file_id = file_id
    )
    file_loader = process_controller.get_file_loader(
        file_id= file_id
    )
    file_content = process_controller.get_file_content(
        file_id = file_id
    )
    file_chunks = process_controller.process_file_content(
        file_id=file_id,
        chunk_size= chunk_size,
        overlap_size= overlap_size
    )
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content= {
                "signal": ResponseSignal.FILE_PROCESSED_FAILED.value,
                "message": "Failed to process the file content."
            }
        )
    
    return file_chunks