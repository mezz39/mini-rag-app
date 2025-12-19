from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
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
from models.ProjectModel import ProjectModel
from models.db_schemas import DataChunk
from models.db_schemas import Asset
from models.ChunkModel import ChunkModel
from bson.objectid import ObjectId
from models.AssetModel import AssetModel
from models.enums.AssetTypeEnums import AssetTypeEnums

logger = logging.getLogger("uvicorn.error")
data_router = APIRouter(prefix= "/api/v1/data",
            tags= ["api_v1", "data"])
@data_router.get("/test")
async def test():
    return {"status": "ok"}

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, 
                      project_id: str, 
                      file: UploadFile, 
                      app_settings: Settings = Depends(get_settings)):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )    
    project  = await project_model.get_project_or_create_one(
        project_id = project_id
    )

    # validate the file type and size
    Data_controller = DataController()
    is_valid = await Data_controller.validate_uploaded_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": is_valid}
        )

    # generate unique filename
    file_path, file_id = Data_controller.generate_unique_filename(
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
    
    asset_model = await AssetModel.create_instance(
        db_client=request.app.state.db_client
    )    
    
    
    
    asset_resource = Asset(
        asset_project_id= project.id,
        asset_type=str(AssetTypeEnums.ASSETFILETYPE.value),
        asset_name=file_id,
        asset_size = os.path.getsize(file_path)
    )
    
    asset_record = await asset_model.create_asset(
        asset= asset_resource
    )

    return JSONResponse(
        content={
            "signal": "File_Upload_Successful",
            "file_id": str(asset_record.id)
        }
    )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, 
                           project_id:str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    
    # Normalize do_reset to int (could arrive as string from request)
    try:
        do_reset = int(do_reset) if do_reset is not None else 0
    except (ValueError, TypeError):
        do_reset = 0

    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id= project_id
    )
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
    
    chunk_model = await ChunkModel.create_instance(
        db_client= request.app.state.db_client
    )
    if do_reset == 1:
        # delete existing chunks for the project
        logger.info(f"=== RESET DEBUG ===")
        logger.info(f"project._id value: {project.id}")
        logger.info(f"project._id type: {type(project.id)}")
        
        # Check how many chunks exist with this project_id
        existing_chunks = await chunk_model.collection.count_documents({"chunk_project_id": project.id})
        logger.info(f"Chunks found with project._id: {existing_chunks}")
        
        # Now delete them
        deleted = await chunk_model.delete_chunks_by_project_id(str(project.id))
        logger.info(f"Deleted {deleted} chunks")
        logger.info(f"=== RESET END ===")
    
    if project.id is None:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content= {
                "signal": ResponseSignal.FILE_PROCESSED_FAILED.value,
                "message": "Project ID is invalid."
            }
        )
    
    file_chunk_records = [
        DataChunk(
            chunk_text= chunk.page_content,
            chunk_metadata= chunk.metadata,
            chunk_order= i+1,
            chunk_project_id= project.id
        )
        for i, chunk in enumerate(file_chunks)
    ]
    no_records = await chunk_model.insert_many_chunks(
        chunks= file_chunk_records,
        batch_size= 100

    )

    return JSONResponse(
        content= {
            "signal": ResponseSignal.FILE_PROCESSED_SUCCESS.value,
            "message": 
                f"File processed successfully with {no_records} chunks stored."
        }
    )
