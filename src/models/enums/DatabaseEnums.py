from enum import Enum

class DatabaseEnums(str, Enum):
    PROJECTS_COLLECTION = "projects"
    DATA_CHUNKS_COLLECTION = "data_chunks"