"""Debug routes for data operations."""
from fastapi import APIRouter, Request
import logging
from controllers import ProcessController
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel

logger = logging.getLogger("uvicorn.error")
debug_router = APIRouter(prefix="/api/v1/debug", tags=["debug"])


@debug_router.get("/chunks/{project_id}")
async def debug_chunks(request: Request, project_id: str):
    """Debug endpoint: Show all chunks for a project and their structure."""
    project_model =await ProjectModel.create_instance(db_client=request.app.state.db_client)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.state.db_client)
    
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    logger.info(f"Project ID type: {type(project.id)}, value: {project.id}")
    
    # Query chunks directly to inspect structure
    chunks = await chunk_model.collection.find({"chunk_project_id": project.id}).to_list(None)
    chunks_str_query = await chunk_model.collection.find({"chunk_project_id": str(project.id)}).to_list(None)
    
    return {
        "project._id": str(project.id),
        "project._id_type": str(type(project.id)),
        "chunks_with_objectid_query": len(chunks),
        "chunks_with_string_query": len(chunks_str_query),
        "first_chunk_sample": str(chunks[0]) if chunks else None,
        "first_chunk_project_id_type": str(type(chunks[0].get("chunk_project_id"))) if chunks else None
    }


@debug_router.post("/delete-chunks/{project_id}")
async def delete_chunks_endpoint(request: Request, project_id: str):
    """Force delete all chunks for a project and verify."""
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    chunk_model = await ChunkModel.create_instance(db_client=request.app.state.db_client)
    
    project = await project_model.get_project_or_create_one(project_id=str(project_id))
    
    # Count before delete
    count_before = await chunk_model.collection.count_documents({"chunk_project_id": project.id})
    logger.info(f"Chunks BEFORE delete: {count_before}")
    
    # Delete
    deleted = await chunk_model.delete_chunks_by_project_id(str(project.id))
    logger.info(f"Deleted: {deleted}")
    
    # Count after delete
    count_after = await chunk_model.collection.count_documents({"chunk_project_id": project.id})
    logger.info(f"Chunks AFTER delete: {count_after}")
    
    return {
        "project._id": str(project.id),
        "count_before": count_before,
        "deleted": deleted,
        "count_after": count_after
    }


@debug_router.get("/process/{project_id}/{file_id}")
async def debug_process(project_id: str, file_id: str):
    """Debug endpoint: Show file processing details."""
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


@debug_router.get("/all-chunks-breakdown")
async def debug_all_chunks(request: Request):
    """Show all chunks grouped by project."""
    chunk_model = await ChunkModel.create_instance(db_client=request.app.state.db_client)
    
    # Total chunks
    total_chunks = await chunk_model.collection.count_documents({})
    
    # Group by project_id and count
    pipeline = [
        {
            "$group": {
                "_id": "$chunk_project_id",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    grouping = await chunk_model.collection.aggregate(pipeline).to_list(None)
    
    return {
        "total_chunks": total_chunks,
        "chunks_by_project": [
            {
                "project_id": str(item["_id"]),
                "chunk_count": item["count"]
            }
            for item in grouping
        ]
    }


@debug_router.post("/wipe-db")
async def wipe_db(request: Request, payload: dict):
    """Dangerous: wipe projects and data_chunks collections.

    Requires JSON body: { "confirm": "WIPE" }
    """
    confirm = payload.get("confirm") if isinstance(payload, dict) else None
    if confirm != "WIPE":
        return {"error": "To wipe the DB send JSON body {\"confirm\": \"WIPE\"}"}

    # Collections to wipe
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    chunk_model = await ChunkModel.create_instance(db_client=request.app.state.db_client)

    proj_res = await project_model.collection.delete_many({})
    chunk_res = await chunk_model.collection.delete_many({})

    return {
        "projects_deleted": proj_res.deleted_count,
        "chunks_deleted": chunk_res.deleted_count
    }
