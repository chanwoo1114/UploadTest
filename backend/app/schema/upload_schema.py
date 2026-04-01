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


class NetworkMetrics(BaseModel):
    '''네트워크 전송 메트릭 (클라이언트 측 측정)'''
    total_mb: float = Field(..., description="총 전송량 (MB)")
    speed_avg_mbps: float = Field(..., description="평균 전송 속도 (MB/s)")


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
    network: NetworkMetrics | None = None

    run_id: str = Field(..., description="테스트 실행 묶음 ID")
    iteration: int = Field(1, description="동일 조건 반복 회차")


class UploadResponse(BaseModel):
    '''업로드 응답'''
    filename: str
    metrics: UploadMetrics


class ChunkSessionRequest(BaseModel):
    '''청크 세션 생성 요청'''
    filename: str
    total_size: int
    chunk_size: int = Field(default=5 * 1024 * 1024, description="청크 크기 (기본 5MB)")
    total_chunks: int


class ChunkSessionResponse(BaseModel):
    '''청크 세션 응답'''
    session_id: str
    filename: str
    total_size: int
    chunk_size: int
    total_chunks: int
    created_at: datetime
    expires_at: datetime


class ChunkUploadResponse(BaseModel):
    '''청크 업로드 응답'''
    session_id: str
    chunk_number: int
    received_size: int
    total_received: int
    remaining_chunks: int


class ChunkStatusResponse(BaseModel):
    '''청크 상태 조회 응답'''
    session_id: str
    filename: str
    total_chunks: int
    uploaded_chunks: list[int]
    remaining_chunks: list[int]
    total_size: int
    uploaded_size: int
    progress_percent: float


class ChunkCompleteResponse(BaseModel):
    '''청크 완료 응답'''
    filename: str
    total_size: int
    total_chunks: int
    metrics: UploadMetrics


class StreamingUploadResponse(BaseModel):
    '''스트리밍 업로드 응답'''
    filename: str
    file_size: int
    metrics: UploadMetrics


class MultipartInitRequest(BaseModel):
    '''멀티파트 초기화 요청'''
    filename: str
    total_size: int
    part_size: int = Field(default=5 * 1024 * 1024, description="파트 크기 (기본 5MB)")


class PartUploadUrl(BaseModel):
    '''파트 업로드 URL 정보'''
    part_number: int
    url: str
    expected_size: int


class MultipartInitResponse(BaseModel):
    '''멀티파트 초기화 응답'''
    upload_id: str
    filename: str
    total_parts: int
    part_size: int
    upload_urls: list[PartUploadUrl]
    created_at: datetime
    expires_at: datetime


class PartUploadResponse(BaseModel):
    '''파트 업로드 응답'''
    upload_id: str
    part_number: int
    etag: str
    size: int


class PartCompleteInfo(BaseModel):
    '''파트 완료 정보'''
    part_number: int
    etag: str
    size: int


class MultipartCompleteRequest(BaseModel):
    '''멀티파트 완료 요청'''
    upload_id: str
    parts: list[PartCompleteInfo]


class MultipartCompleteResponse(BaseModel):
    '''멀티파트 완료 응답'''
    file_id: str
    filename: str
    total_size: int
    total_parts: int
    metrics: UploadMetrics


class BenchmarkRequest(BaseModel):
    '''벤치마크 요청'''
    file_sizes_mb: list[int] = Field(default=[1, 10, 50], description="테스트할 파일 크기 (MB)")
    methods: list[UploadMethod] = Field(default=list(UploadMethod), description="테스트할 방식")
    iterations: int = Field(default=1, ge=1, le=10, description="반복 횟수")
    chunk_size_mb: int = Field(default=5, description="청크/파트 크기 (MB)")
    concurrency: int = Field(default=4, ge=1, le=16, description="S3 병렬 업로드 수")


class BenchmarkSizeResult(BaseModel):
    '''특정 크기에 대한 벤치마크 결과'''
    file_size_mb: int
    results: dict[str, list[UploadMetrics]]


class BenchmarkSummary(BaseModel):
    '''벤치마크 전체 결과'''
    run_id: str
    started_at: datetime
    completed_at: datetime
    total_tests: int
    results: list[BenchmarkSizeResult]
    recommendations: dict[str, str]