import time
import uuid
import psutil
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from app.schema.upload_schema import (
    UploadMethod,
    UploadMetrics,
    TimeBreakdown,
    TimeSample,
    CpuMetrics,
    MemoryMetrics,
)

logger = logging.getLogger(__name__)


@dataclass
class MetricsCollector:
    '''업로드 메트릭 수집기'''
    method: UploadMethod
    file_size_bytes: int
    run_id: str = ""
    iteration: int = 1

    _start_time: float = field(default=0.0, init=False)
    _end_time: float = field(default=0.0, init=False)
    _upload_end_time: float = field(default=0.0, init=False)
    _started_at: datetime = field(default_factory=datetime.now, init=False)
    _completed_at: datetime | None = field(default=None, init=False)

    _cpu_samples: list[tuple[float, float]] = field(default_factory=list, init=False)
    _memory_samples: list[tuple[float, float]] = field(default_factory=list, init=False)
    _memory_baseline: float = field(default=0.0, init=False)

    _chunk_size_bytes: int | None = field(default=None, init=False)
    _chunk_count: int | None = field(default=None, init=False)
    _concurrency: int | None = field(default=None, init=False)

    _success: bool = field(default=True, init=False)
    _error_message: str | None = field(default=None, init=False)

    def start(self) -> None:
        '''측정 시작'''
        self._start_time = time.perf_counter()
        self._started_at = datetime.now()
        if not self.run_id:
            self.run_id = uuid.uuid4().hex[:12]

        try:
            psutil.Process().cpu_percent(interval=None)
        except Exception:
            pass

        self._memory_baseline = self._get_memory_mb()
        self.sample()
        logger.debug(f"Metrics collection started for {self.method.value}")

    def mark_upload_done(self) -> None:
        '''업로드(전송) 완료 시점 기록'''
        self._upload_end_time = time.perf_counter()

    def stop(self) -> None:
        '''측정 종료'''
        self._end_time = time.perf_counter()
        self._completed_at = datetime.now()
        if not self._upload_end_time:
            self._upload_end_time = self._end_time
        self.sample()
        logger.debug(f"Metrics collection stopped for {self.method.value}")

    def sample(self) -> None:
        '''CPU, 메모리 시계열 샘플 수집'''
        elapsed = time.perf_counter() - self._start_time if self._start_time else 0.0
        try:
            proc = psutil.Process()
            cpu = proc.cpu_percent(interval=None)
            self._cpu_samples.append((elapsed, cpu))

            mem_mb = proc.memory_info().rss / (1024 * 1024)
            self._memory_samples.append((elapsed, mem_mb))
        except Exception as e:
            logger.warning(f"Failed to sample metrics: {e}")

    def set_chunk_info(self, chunk_size: int, chunk_count: int) -> None:
        '''청크/파트 정보 설정'''
        self._chunk_size_bytes = chunk_size
        self._chunk_count = chunk_count

    def set_concurrency(self, concurrency: int) -> None:
        '''동시성 설정'''
        self._concurrency = concurrency

    def set_error(self, message: str) -> None:
        '''에러 설정'''
        self._success = False
        self._error_message = message

    def build_metrics(self) -> UploadMetrics:
        '''최종 메트릭 생성 (미종료 시 자동 종료)'''
        if not self._end_time:
            self.stop()

        total_sec = self._end_time - self._start_time
        upload_sec = self._upload_end_time - self._start_time if self._upload_end_time else total_sec
        processing_sec = max(0.0, total_sec - upload_sec)

        return UploadMetrics(
            method=self.method,
            file_size_bytes=self.file_size_bytes,
            started_at=self._started_at,
            completed_at=self._completed_at or datetime.now(),
            success=self._success,
            error_message=self._error_message,
            time=TimeBreakdown(
                total_sec=round(total_sec, 6),
                upload_sec=round(upload_sec, 6),
                processing_sec=round(processing_sec, 6),
            ),
            chunk_size_bytes=self._chunk_size_bytes,
            chunk_count=self._chunk_count,
            concurrency=self._concurrency,
            cpu=self._build_cpu(),
            memory=self._build_memory(),
            run_id=self.run_id,
            iteration=self.iteration,
        )

    def _build_cpu(self) -> CpuMetrics:
        '''CPU 메트릭 + 시계열 빌드'''
        values = [v for _, v in self._cpu_samples]
        if not values:
            return CpuMetrics(peak=0.0, avg=0.0, samples=[])
        return CpuMetrics(
            peak=round(max(values), 2),
            avg=round(sum(values) / len(values), 2),
            samples=[TimeSample(elapsed_sec=round(t, 6), value=round(v, 2)) for t, v in self._cpu_samples],
        )

    def _build_memory(self) -> MemoryMetrics:
        '''메모리 메트릭 + baseline + 시계열 빌드'''
        values = [v for _, v in self._memory_samples]
        if not values:
            return MemoryMetrics(baseline_mb=0.0, peak=0.0, avg=0.0, samples=[])
        return MemoryMetrics(
            baseline_mb=round(self._memory_baseline, 2),
            peak=round(max(values), 2),
            avg=round(sum(values) / len(values), 2),
            samples=[TimeSample(elapsed_sec=round(t, 6), value=round(v, 2)) for t, v in self._memory_samples],
        )

    @staticmethod
    def _get_memory_mb() -> float:
        '''현재 프로세스 메모리 (MB)'''
        try:
            return psutil.Process().memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0


@asynccontextmanager
async def track_metrics(
    method: UploadMethod,
    file_size_bytes: int,
    run_id: str = "",
    iteration: int = 1,
):
    '''메트릭 수집 컨텍스트 매니저'''
    collector = MetricsCollector(
        method=method,
        file_size_bytes=file_size_bytes,
        run_id=run_id,
        iteration=iteration,
    )
    collector.start()
    try:
        yield collector
    finally:
        collector.stop()


class ProgressTracker:
    '''진행률 추적 + 주기적 샘플링'''

    def __init__(self, total_size: int, collector: MetricsCollector | None = None):
        self.total_size = total_size
        self.current_size = 0
        self.collector = collector
        self._last_sample = time.perf_counter()
        self._sample_interval = 0.25  # 250ms마다 샘플링

    def update(self, bytes_received: int) -> float:
        '''진행률 업데이트 + 필요 시 샘플링'''
        self.current_size += bytes_received
        now = time.perf_counter()

        if self.collector and (now - self._last_sample) >= self._sample_interval:
            self.collector.sample()
            self._last_sample = now

        return self.get_progress()

    def get_progress(self) -> float:
        '''현재 진행률 반환'''
        return (self.current_size / self.total_size) * 100 if self.total_size > 0 else 0