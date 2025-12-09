from BaseController import BaseController
from fastapi import FastAPI, APIRouter, Depends, UploadFile
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576

    async def validate_uploaded_file(self, file: UploadFile):
        contents = await file.read()
        file_size = len(contents)
        if file.content_type not in self.app_settings.ALLOWED_FILE_TYPES :
            raise ValueError(f"File type {file.content_type} is not allowed.")

        if file_size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            raise ValueError(f"File size exceeds the maximum limit of {self.app_settings.FILE_MAX_SIZE} MB.")
        
        return True