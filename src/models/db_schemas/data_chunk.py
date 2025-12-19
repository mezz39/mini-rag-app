from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order :int = Field(..., gt=0)
    chunk_project_id : ObjectId

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )

    @classmethod

    def get_indexes(cls):

        return [
            {
                "key": [
                    ("chunk_project_id", 1)
                ],
                "name": "chunk_project_id_index_1",
                "unique": False
            }
        ]    