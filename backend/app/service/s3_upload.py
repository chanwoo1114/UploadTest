import uuid
import logging
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from app.utils.metrics import MetricsCollector

@dataclass
class S3Session:
    '''S3 스타일 업로드 세션'''
    upload_id: str
    filename: str
    total_size: int
    part_size: int
    total_parts: int
    concurrency: int
    created_at: datetime
    expires_at: datetime
    uploaded_parts: dict[int, dict] = field(default_factory=dict)


class S3UploadService:
    '''S3 스타일 업로드 서비스 - 병렬 파트 업로드, ETag 검증'''

    _sessions: dict[str, S3Session] = {}
    _collectors: dict[str, MetricsCollector] = {}

    @classmethod
    async def init_upload(
        cls,
        request,
        run_id: str = "",
    ):