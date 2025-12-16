from .BaseController import BaseController
from .ProjectController import ProjectController
import os 
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models.enums.processingEnums import ProcessingEnum
from helpers import get_settings, Settings
from typing import Optional
class ProcessController(BaseController) :
    def __init__(self, project_id:str):
        super().__init__()
    
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id= self.project_id)

    def get_file_path(self, file_id: str):
        file_path = os.path.join(
            self.project_path, 
            file_id
        )
        return file_path

    def get_file_extension(self, file_id: str):
        file_path = self.get_file_path(file_id= file_id)
        _, file_extension = os.path.splitext(file_path)
        
        return file_extension.lower()

    def get_file_loader(self, file_id:str):

        file_ext = self.get_file_extension(file_id=file_id)
        file_path = self.get_file_path(file_id=file_id)

        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        elif file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)

        return None

    def get_file_content(self, file_id:str):

        loader = self.get_file_loader(file_id=file_id)
    
        if loader is None:
            return None

        documents = loader.load()
        return documents

    def process_file_content(self, file_id:str, 
                             chunk_size:Optional[int]=100, 
                             overlap_size:Optional[int]=20):

        documents = self.get_file_content(file_id=file_id)

        if documents is None:
            return None

        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size= chunk_size,
            chunk_overlap= overlap_size,
            length_function= len,
            separators= ["\n\n", "\n", " ", ""]
        )
        
        documents_text = [doc.page_content for doc in documents]
        documents_meta_data = [doc.metadata for doc in documents]

        chunks = text_splitter.create_documents(
            texts=documents_text,
            metadatas=documents_meta_data
        )

        return chunks