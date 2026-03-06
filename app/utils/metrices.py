import asyncio
import os
from contextlib import asynccontextmanager

import psutil
import time
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from app.schema.upload_schema import UploadMethod, UploadMetrics


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

    _start_disk_time: int = 0
    _end_disk_time: int = 0

    _sampling_task: Optional[asyncio.Task] = None
    _is_collecting: bool = False

    _process: psutil.Process = field(default_factory=psutil.Process)

    def start(self):
        '''측정 시작'''
        self._start_time = time.perf_counter()
        self._started_at = datetime.now()
        self._is_collecting = True
        self._sample_metrics()

    def stop(self):
        '''측정 종료'''
        self._end_time = time.perf_counter()
        self._completed_at = datetime.now()
        self._is_collecting = False
        self._sample_metrics()

    def _sample_metrics(self):
        '''메모리, CPU 측정'''
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        self._memory_samples.append(memory_mb)

    async def start_continue_sampling(self, interval: float = 0.1):
        '''연속 메모리, CPU 수집'''
        self.is_collecting = True

        async def _sample_loop():
            while True:
                self._sample_metrics()
                print(self._memory_samples)
                await asyncio.sleep(interval)

        self._sampling_task = asyncio.create_task(_sample_loop())

    def stop_continuous_sampling(self):
        """연속 메모리 수집 중지"""
        self._is_collecting = False
        if self._sampling_task:
            self._sampling_task.cancel()

    def get_metrics(self):
        if self._end_time is None:
            self.stop()

        total_time = self._end_time - self._start_time
        throughput_mbps = (self.file_size / (1024 * 1024) / total_time if total_time > 0 else 0)

        memory_peak = max(self._memory_samples if self._memory_samples else 0)
        memory_avg = sum(self._memory_samples) / len(self._memory_samples) if self._memory_samples else 0


@asynccontextmanager
async def track_metrics(method: UploadMethod, file_size: int, continue_sampling: bool = True):
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