from .BaseDataModel import BaseDataModel
from .db_schemas import Asset
from .enums.DatabaseEnums import DatabaseEnums
from bson.objectid import ObjectId

class AssetModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnums.COLLECTION_ASSET_NAME.value]
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    async def init_collection(self) :
        all_collections = await self.db_client.list_collection_names()
        if DatabaseEnums.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = self.db_client[DatabaseEnums.COLLECTION_ASSET_NAME.value]
        indexes = Asset.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                ) 

    async def create_asset(self, asset:Asset):  
        result = await self.collection.insert_one(
            asset.model_dump()
        )      
        asset.id = result.inserted_id
        return asset
    async def get_all_project_assets(self, assets_project_id, assets_type):

        records = await self.collection.find_one(
            {
                "assets_project_id":ObjectId(assets_project_id) 
                                          if isinstance(assets_project_id, str)  
                                          else assets_project_id,
                "assets_type":assets_type
            }
        )
        return [
            Asset(**records)
            for record in records
        ]
