import uuid
import hashlib
import logging
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from app.schema.upload_schema import (
    UploadMethod,
    MultipartInitRequest,
    MultipartInitResponse,
    PartUploadUrl,
    PartUploadResponse,
    MultipartCompleteRequest,
    MultipartCompleteResponse,
)

from app.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)

@dataclass
class MultipartSession:
    '''멀티파트 업로드 세션'''
    upload_id: str
    filename: str
    total_size: int
    part_size: int
    total_parts: int
    created_at: datetime
    expires_at: datetime
    uploaded_parts: dict[int, dict] = field(default_factory=dict)


class MultipartUploadService:
    '''Multipart 업로드 서비스 - S3 스타일 병렬 업로드'''

    _sessions: dict[str, MultipartSession] = {}
    _collectors: dict[str, MetricsCollector] = {}

    @classmethod
    async def init_upload(cls, request: MultipartInitRequest) -> MultipartInitResponse:
        upload_id = str(uuid.uuid4())
        now = datetime.now()
        expires_at = now + timedelta(hours=24)

        total_parts = (request.total_parts + request.part_size -1) // request.part_size

        session = MultipartSession(
            upload_id=upload_id,
            filename=request.filename,
            total_size=request.total_parts,
            part_size=request.part_size,
            total_parts=total_parts,
            created_at=now,
            expires_at=expires_at,
            uploaded_parts=request.uploaded_parts,
        )

        cls._sessions[upload_id] = session



