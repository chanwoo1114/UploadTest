from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class UploadMethod(str, Enum):
    SIMPLE = "simple"

class UploadMetrics(BaseModel):
    method: UploadMethod
    file_size: int
    total_time: float
    memory: float
    started_at: datetime
    completed_at: datetime
    success: bool

class UploadResponse(BaseModel):
    filename: str
    file_size: int
    method: UploadMethod
