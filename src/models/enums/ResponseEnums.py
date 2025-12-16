from enum import Enum

class ResponseSignal(Enum):

    FILE_TYPE_NOT_SUPPORTED = "file type not supported"
    FILE_SIZE_EXCEEDS_LIMIT = "file size exceeds limit"
    FILE_UPLOAD_SUCCESS = "file uploaded successfully"
    FILE_UPLOAD_FAILED = "file upload failed"
    FILE_VALIDATED_SUCCESS = "file validated successfully"
    FILE_VALIDATED_FAILED = "file validation failed"
    FILE_PROCESSED_SUCCESS = "file processed successfully"
    FILE_PROCESSED_FAILED = "file processing failed"
    
    
