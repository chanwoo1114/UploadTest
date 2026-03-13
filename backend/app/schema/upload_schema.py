from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class UploadMethod(str, Enum):
    SIMPLE = "simple"
    STREAMING = "streaming"
    CHUNKED = "chunked"
    S3 = "s3"


class TimeSample(BaseModel):
    '''시계열 샘플 포인트'''
    elapsed_sec: float = Field(..., description="시작 시점 기준 경과 시간 (초)")
    value: float = Field(..., description="측정값")


class CpuMetrics(BaseModel):
    '''CPU 사용량'''
    peak: float = Field(..., description="최대 CPU 점유율 (%)")
    avg: float = Field(..., description="평균 CPU 점유율 (%)")
    samples: list[TimeSample] = Field(default_factory=list, description="시계열 CPU 샘플")


class MemoryMetrics(BaseModel):
    '''메모리 사용량'''
    baseline_mb: float = Field(..., description="업로드 시작 시점 메모리 (MB)")
    peak: float = Field(..., description="최대 메모리 사용량 (MB)")
    avg: float = Field(..., description="평균 메모리 사용량 (MB)")
    samples: list[TimeSample] = Field(default_factory=list, description="시계열 메모리 샘플")


class TimeBreakdown(BaseModel):
    '''시간 분석'''
    total_sec: float = Field(..., description="전체 소요 시간 (초)")
    upload_sec: float = Field(..., description="순수 전송 시간 (초)")
    processing_sec: float = Field(..., description="서버 후처리 시간 (초)")


class UploadMetrics(BaseModel):
    '''업로드 성능 메트릭'''
    method: UploadMethod
    file_size_bytes: int
    started_at: datetime
    completed_at: datetime
    success: bool
    error_message: str | None = None

    time: TimeBreakdown

    chunk_size_bytes: int | None = None
    chunk_count: int | None = None
    concurrency: int | None = None

    cpu: CpuMetrics
    memory: MemoryMetrics

    run_id: str = Field(..., description="테스트 실행 묶음 ID")
    iteration: int = Field(1, description="동일 조건 반복 회차")


class UploadResponse(BaseModel):
    '''업로드 응답'''
    filename: str
    metrics: UploadMetrics