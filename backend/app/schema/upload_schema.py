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


class TimeBreakdown(BaseModel):
    total_sec: float = Field(..., description="전체 소요 시간 (초)")
    upload_sec: float = Field(..., description="순수 전송 시간 (초)")
    processing_sec: float = Field(..., description="서버 후처리 시간 (초)")


class UploadMetrics(BaseModel):
    method: UploadMethod
    file_size_bytes: int
    target_file_size_mb: float
    app_avg_speed_mb_s: float
    started_at: datetime
    completed_at: datetime
    success: bool

    error_message: str | None = None
    retry_count: int = 0

    time: TimeBreakdown

    chunk_size_bytes: int | None = None
    chunk_count: int | None = None
    concurrency: int | None = None

    cpu: CpuMetrics
    memory: MemoryMetrics
    disk: DiskMetrics
    network: NetworkMetrics

    run_id: str = Field(..., description="테스트 실행 묶음 ID")
    iteration: int = Field(1, description="동일 조건 반복 회차")


class UploadResponse(BaseModel):
    filename: str
    metrics: UploadMetrics
