from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    asset_project_id: ObjectId
    asset_name:str = Field(..., min_length=1)
    asset_type:str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default_factory=int)
    asset_config:dict = Field(default_factory=dict)
    asset_pushed_at: datetime = Field(default_factory=datetime.now)



    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )


    @classmethod

    def get_indexes(cls):

        return [
            {
                "key": [
                    ("asset_project_id", 1)
                ],
                "name": "asset_project_id_index_1",
                "unique": False
            },
            {
                "key": [
                    ("asset_project_id", 1),
                    ("asset_name", 1)
                ],
                "name": "asset_project_id_asset_name_index_1",
                "unique": True
            }
        ]    




        
    