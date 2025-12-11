from . import BaseController
from .ProjectController import ProjectController
from fastapi import FastAPI, APIRouter, Depends, UploadFile
from models.enums.ResponseEnums import ResponseSignal
import os
import re
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576
    async def validate_uploaded_file(self, file: UploadFile):
        contents = await file.read()
        file_size = len(contents)
        if file.content_type not in self.app_settings.ALLOWED_FILE_TYPES :
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file_size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDS_LIMIT.value
        
        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value
        
    def generate_unique_filename(self, original_filename: str, project_id:str) :
        random_key= self.generate_random_string()  
        project_path = ProjectController().get_project_path(project_id = project_id)

        cleaned_filename = self.get_clean_filename(
            original_filename = original_filename
        )

        new_file_path = os.path.join(
            project_path,
            random_key, cleaned_filename
        )

        while os.path.exists(new_file_path):
            random_key= self.generate_random_string()  
            new_file_path = os.path.join(
                project_path,
                random_key, '_', cleaned_filename
            )
        return new_file_path, random_key + '_' + cleaned_filename

    
    def get_clean_filename(self, original_filename: str) -> str:
        # Remove any character that is NOT a letter, number, dot, underscore, or hyphen
        cleaned_filename = original_filename.replace(" ", "_")

    # Optional: collapse multiple underscores
        cleaned_filename = re.sub(r"[^A-Za-z0-9._-]", "", original_filename) # Prevent directory traversal

        return cleaned_filename
    



    