from .BaseDataModel import BaseDataModel
from .db_schemas import DataChunk
from .enums.DatabaseEnums import DatabaseEnums
from bson.objectid import ObjectId
from pymongo import InsertOne
class ChunkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnums.COLLECTION_DATA_CHUNKS.value]
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DatabaseEnums.COLLECTION_DATA_CHUNKS.value not in all_collections:
            self.collection = self.db_client[DatabaseEnums.COLLECTION_DATA_CHUNKS.value]
        indexes = self.collection.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )    
    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(
            chunk.model_dump(by_alias=True, exclude_unset=True)
        )
        chunk._id = result.inserted_id
        return chunk
    
    async def get_chunk_by_id(self, chunk_id:str):
        result = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })

        return DataChunk(**result) if result else None
    
    async def insert_many_chunks(self, chunks:list, batch_size:int=100):

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            operations = [
                InsertOne(chunk.model_dump())
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)

        return len(chunks)
    
    async def delete_chunks_by_project_id(self, project_id):
        """Delete all chunks for a project. Accepts ObjectId or string."""
        # Handle both ObjectId and string inputs
        if isinstance(project_id, str):
            try:
                project_id = ObjectId(project_id)
            except Exception as e:
                print(f"Error converting project_id to ObjectId: {e}")
                return 0
        
        # Now delete with the ObjectId
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })
        return result.deleted_count