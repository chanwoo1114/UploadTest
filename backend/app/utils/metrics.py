import asyncio
from contextlib import asynccontextmanager
import psutil
import time
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from app.schema.upload_schema import (
    UploadMethod, UploadMetrics,
    CpuMetrics, MemoryMetrics, DiskMetrics, NetworkMetrics
)


@dataclass
class MetricsCollector:
    method: UploadMethod
    file_size: int

    _start_time: Optional[float] = None
    _end_time: Optional[float] = None

    _started_at: Optional[datetime] = None
    _completed_at: Optional[datetime] = None

    _memory_samples: list[float] = field(default_factory=list)
    _cpu_samples: list[float] = field(default_factory=list)

    _disk_speed_samples: list[float] = field(default_factory=list)
    _net_speed_samples: list[float] = field(default_factory=list)

    _start_disk_write: int = 0
    _end_disk_write: int = 0

    _start_net_recv: int = 0
    _end_net_recv: int = 0

    _prev_time: float = 0.0
    _prev_disk_write: int = 0
    _prev_net_recv: int = 0

    _sampling_task: Optional[asyncio.Task] = None
    _is_collecting: bool = False

    _process: psutil.Process = field(default_factory=psutil.Process)

    def start(self):
        '''측정 시작'''
        self._process.cpu_percent()

        self._start_disk_write = self._get_disk_write_bytes()
        self._start_net_recv = psutil.net_io_counters().bytes_recv
        self._start_time = time.perf_counter()

        self._prev_disk_write = self._start_disk_write
        self._prev_net_recv = self._start_net_recv
        self._prev_time = self._start_time

        self._started_at = datetime.now()
        self._is_collecting = True
        self._sample_metrics()

    def stop(self):
        '''측정 종료'''
        self._end_time = time.perf_counter()
        self._completed_at = datetime.now()
        self._is_collecting = False

        self._end_disk_write = self._get_disk_write_bytes()
        self._end_net_recv = psutil.net_io_counters().bytes_recv

        self._sample_metrics()

    def _get_disk_write_bytes(self):
        '''현재 프로세스의 누적 디스크 쓰기 바이트 반환'''
        try:
            return self._process.io_counters().write_bytes
        except (AttributeError, psutil.AccessDenied):
            return 0

    def _sample_metrics(self):
        '''메모리, CPU 및 디스크/네트워크 순간 속도 측정'''
        memory_mb = self._process.memory_info().rss / (1024 * 1024)
        self._memory_samples.append(memory_mb)

        cpu_percent = self._process.cpu_percent()
        self._cpu_samples.append(cpu_percent)

        current_time = time.perf_counter()
        current_disk = self._get_disk_write_bytes()
        current_net = psutil.net_io_counters().bytes_recv

        time_delta = current_time - self._prev_time

        if time_delta > 0:
            disk_speed_mb_s = ((current_disk - self._prev_disk_write) / time_delta) / (1024 * 1024)
            net_speed_mb_s = ((current_net - self._prev_net_recv) / time_delta) / (1024 * 1024)

            self._disk_speed_samples.append(disk_speed_mb_s)
            self._net_speed_samples.append(net_speed_mb_s)

        self._prev_time = current_time
        self._prev_disk_write = current_disk
        self._prev_net_recv = current_net

    async def start_continue_sampling(self, interval: float = 0.1):
        '''연속 지표 수집'''
        self._is_collecting = True

        async def _sample_loop():
            try:
                while self._is_collecting:
                    self._sample_metrics()
                    await asyncio.sleep(interval)
            except asyncio.CancelledError:
                pass

        self._sampling_task = asyncio.create_task(_sample_loop())

    def stop_continuous_sampling(self):
        """연속 지표 수집 중지"""
        self._is_collecting = False
        if self._sampling_task:
            self._sampling_task.cancel()

    def get_summary(self, success: bool = True) -> UploadMetrics:
        '''최종 결과 요약'''
        total_time = self._end_time - self._start_time if self._end_time else 0.0

        target_size_mb = self.file_size / (1024 * 1024)
        app_avg_speed = target_size_mb / total_time if total_time > 0 else 0

        calc_max = lambda samples: round(max(samples), 2) if samples else 0.0
        calc_avg = lambda samples: round(sum(samples) / len(samples), 2) if samples else 0.0

        disk_total_mb = (self._end_disk_write - self._start_disk_write) / (1024 * 1024)
        net_total_mb = (self._end_net_recv - self._start_net_recv) / (1024 * 1024)

        return UploadMetrics(
            method=self.method,
            file_size_bytes=self.file_size,
            target_file_size_mb=round(target_size_mb, 2),
            total_time_sec=round(total_time, 3),
            app_avg_speed_mb_s=round(app_avg_speed, 2),
            started_at=self._started_at or datetime.now(),
            completed_at=self._completed_at or datetime.now(),
            success=success,

            cpu=CpuMetrics(
                peak=calc_max(self._cpu_samples),
                avg=calc_avg(self._cpu_samples)
            ),
            memory=MemoryMetrics(
                peak=calc_max(self._memory_samples),
                avg=calc_avg(self._memory_samples)
            ),
            disk=DiskMetrics(
                total_mb=round(disk_total_mb, 2),
                speed_peak=calc_max(self._disk_speed_samples),
                speed_avg=round(disk_total_mb / total_time, 2) if total_time > 0 else 0.0
            ),
            network=NetworkMetrics(
                total_mb=round(net_total_mb, 2),
                speed_peak=calc_max(self._net_speed_samples),
                speed_avg=round(net_total_mb / total_time, 2) if total_time > 0 else 0.0
            )
        )


@asynccontextmanager
async def track_metrics(method: str, file_size: int, continue_sampling: bool = True):
    collector = MetricsCollector(method=method, file_size=file_size)
    collector.start()

    if continue_sampling:
        await collector.start_continue_sampling()

    try:
        yield collector

    finally:
        if continue_sampling:
            collector.stop_continuous_sampling()
        collector.stop()
