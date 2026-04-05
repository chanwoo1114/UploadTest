import uuid
import hashlib
import logging
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from app.schema.upload_schema import (
    UploadMethod,
    S3InitRequest,
    S3InitResponse,
    PartUploadUrl,
    PartUploadResponse,
    S3CompleteRequest,
    S3CompleteResponse,
)
from app.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


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
        request: S3InitRequest,
        base_dir: Path,
        run_id: str = "",
        iteration: int = 1,
    ) -> S3InitResponse:
        '''S3 업로드 초기화'''
        upload_id = str(uuid.uuid4())
        now = datetime.now()
        expires_at = now + timedelta(hours=24)

        total_parts = (request.total_size + request.part_size - 1) // request.part_size

        session = S3Session(
            upload_id=upload_id,
            filename=request.filename,
            total_size=request.total_size,
            part_size=request.part_size,
            total_parts=total_parts,
            concurrency=request.concurrency,
            created_at=now,
            expires_at=expires_at,
        )
        cls._sessions[upload_id] = session

        collector = MetricsCollector(
            method=UploadMethod.S3,
            file_size_bytes=request.total_size,
            run_id=run_id,
            iteration=iteration,
        )
        collector.start()
        collector.set_chunk_info(request.part_size, total_parts)
        collector.set_concurrency(request.concurrency)
        cls._collectors[upload_id] = collector

        part_dir = base_dir / upload_id
        part_dir.mkdir(parents=True, exist_ok=True)

        upload_urls: list[PartUploadUrl] = []
        remaining = request.total_size
        for i in range(1, total_parts + 1):
            expected = min(request.part_size, remaining)
            remaining -= expected
            upload_urls.append(PartUploadUrl(
                part_number=i,
                url=f"/api/s3/{upload_id}/parts/{i}",
                expected_size=expected,
            ))

        logger.info(f"S3 upload initialized: {upload_id} ({total_parts} parts, concurrency={request.concurrency})")

        return S3InitResponse(
            upload_id=upload_id,
            filename=request.filename,
            total_parts=total_parts,
            part_size=request.part_size,
            concurrency=request.concurrency,
            upload_urls=upload_urls,
            created_at=now,
            expires_at=expires_at,
        )

    @classmethod
    async def upload_part(
        cls,
        upload_id: str,
        part_number: int,
        part_data: bytes,
        base_dir: Path,
    ) -> PartUploadResponse:
        '''파트 업로드'''
        session = cls._sessions.get(upload_id)
        if not session:
            raise ValueError(f"Upload not found: {upload_id}")

        if part_number < 1 or part_number > session.total_parts:
            raise ValueError(f"Invalid part number: {part_number}")

        etag = hashlib.md5(part_data).hexdigest()

        part_dir = base_dir / upload_id
        part_path = part_dir / f"part_{part_number:05d}"
        async with aiofiles.open(part_path, "wb") as f:
            await f.write(part_data)

        session.uploaded_parts[part_number] = {"etag": etag, "size": len(part_data)}

        collector = cls._collectors.get(upload_id)
        if collector:
            collector.sample()

        logger.debug(f"Part {part_number}/{session.total_parts} uploaded for {upload_id}")

        return PartUploadResponse(
            upload_id=upload_id,
            part_number=part_number,
            etag=etag,
            size=len(part_data),
        )

    @classmethod
    async def complete_upload(cls, request: S3CompleteRequest, base_dir: Path) -> S3CompleteResponse:
        '''S3 업로드 완료 및 병합'''
        session = cls._sessions.get(request.upload_id)
        if not session:
            raise ValueError(f"Upload not found: {request.upload_id}")

        for part_info in request.parts:
            stored = session.uploaded_parts.get(part_info.part_number)
            if not stored:
                raise ValueError(f"Part {part_info.part_number} not uploaded")
            if stored["etag"] != part_info.etag:
                raise ValueError(f"ETag mismatch for part {part_info.part_number}")

        collector = cls._collectors.get(request.upload_id)
        if collector:
            collector.mark_upload_done()

        file_id = str(uuid.uuid4())
        s3_dir = base_dir / "s3"
        s3_dir.mkdir(parents=True, exist_ok=True)
        final_path = s3_dir / f"{file_id}_{session.filename}"
        part_dir = base_dir / request.upload_id

        total_size = 0
        async with aiofiles.open(final_path, "wb") as outfile:
            for i in range(1, session.total_parts + 1):
                part_path = part_dir / f"part_{i:05d}"
                async with aiofiles.open(part_path, "rb") as infile:
                    content = await infile.read()
                    await outfile.write(content)
                    total_size += len(content)

        import shutil
        shutil.rmtree(part_dir, ignore_errors=True)

        if collector:
            collector.stop()
            metrics = collector.build_metrics()
        else:
            fallback = MetricsCollector(UploadMethod.S3, total_size)
            fallback.start()
            fallback.stop()
            metrics = fallback.build_metrics()

        cls._sessions.pop(request.upload_id, None)
        cls._collectors.pop(request.upload_id, None)

        logger.info(f"S3 upload completed: {file_id} ({session.total_parts} parts)")

        return S3CompleteResponse(
            filename=session.filename,
            total_size=total_size,
            total_parts=session.total_parts,
            metrics=metrics,
        )

    @classmethod
    async def abort_upload(cls, upload_id: str, base_dir: Path) -> None:
        '''S3 업로드 취소'''
        session = cls._sessions.pop(upload_id, None)
        cls._collectors.pop(upload_id, None)

        if session:
            part_dir = base_dir / upload_id
            if part_dir.exists():
                import shutil
                shutil.rmtree(part_dir)
            logger.info(f"S3 upload aborted: {upload_id}")