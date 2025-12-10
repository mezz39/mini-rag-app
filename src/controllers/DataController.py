from . import BaseController
from fastapi import FastAPI, APIRouter, Depends, UploadFile
from models import ResponseSignal
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576
    async def validate_uploaded_file(self, file: UploadFile):
        contents = await file.read()
        file_size = len(contents)
        if file.content_type not in self.app_settings.ALLOWED_FILE_TYPES :
            return False, ResponseSignal.FIle_Type_Not_Supported

        if file_size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FIle_Size_Exceeds_Limit
        return True
    