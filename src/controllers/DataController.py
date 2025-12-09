from .BaseController import BaseController
from fastapi import FastAPI, APIRouter, Depends, UploadFile
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.ALLOWED_FILE_TYPES :
            raise ValueError(f"File type {file.content_type} is not allowed.")

        if file.size > self.app_settings.FILE_MAX_SIZE:
            raise ValueError(f"File size exceeds the maximum limit of {self.app_settings.FILE_MAX_SIZE} MB.")
        
        return True