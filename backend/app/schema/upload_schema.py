from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class UploadMethod(str, Enum):
    SIMPLE = "simple"
    STREAMING = "streaming"
    CHUNKED = "chunked"
    S3 = "s3"


class CpuMetrics(BaseModel):
    peak: float = Field(..., description="최대 CPU 점유율 (%)")
    avg: float = Field(..., description="평균 CPU 점유율 (%)")


class MemoryMetrics(BaseModel):
    peak: float = Field(..., description="최대 메모리 사용량 (MB)")
    avg: float = Field(..., description="평균 메모리 사용량 (MB)")


class DiskMetrics(BaseModel):
    total_mb: float = Field(..., description="디스크 총 쓰기량 (MB)")
    speed_peak: float = Field(..., description="최대 디스크 쓰기 속도 (MB/s)")
    speed_avg: float = Field(..., description="평균 디스크 쓰기 속도 (MB/s)")


class NetworkMetrics(BaseModel):
    total_mb: float = Field(..., description="네트워크 총 수신량 (MB)")
    speed_peak: float = Field(..., description="최대 네트워크 수신 속도 (MB/s)")
    speed_avg: float = Field(..., description="평균 네트워크 수신 속도 (MB/s)")


class UploadMetrics(BaseModel):
    method: UploadMethod
    file_size_bytes: int
    target_file_size_mb: float
    total_time_sec: float
    app_avg_speed_mb_s: float
    started_at: datetime
    completed_at: datetime
    success: bool

    cpu: CpuMetrics
    memory: MemoryMetrics
    disk: DiskMetrics
    network: NetworkMetrics


class UploadResponse(BaseModel):
    filename: str
    metrics: UploadMetrics
