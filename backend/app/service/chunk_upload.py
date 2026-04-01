import uuid
import logging
import aiofiles
import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

from app.schema.upload_schema import (
    UploadMethod,
    ChunkSessionRequest,
    ChunkSessionResponse,
    ChunkUploadResponse,
    ChunkStatusResponse,
    ChunkCompleteResponse,
)
from app.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)

@dataclass
class ChunkSession:
    '''청크 업로드 세션'''
    session_id: str
    filename: str
    total_size: int
    chunk_size: int
    total_chunks: int
    created_at: datetime
    expires_at: datetime
    uploaded_chunks: list[int] = field(default_factory=list)
    uploaded_size: int = 0

    def to_dict(self) -> dict:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["expires_at"] = self.expires_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "ChunkSession":
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)



class ChunkedUploadService:
    '''Chunk 업로드 서비스'''
    _sessions: dict[str, ChunkSession] = {}
    _collectors: dict[str, MetricsCollector] = {}

    @classmethod
    async def create_session(
        cls,
        request: ChunkSessionRequest,
        base_dir: Path,
        run_id: str = "",
        iteration: int = 1,
    ) -> ChunkSessionResponse:
        '''새 청크 세션 생성'''
        session_id = str(uuid.uuid4())
        now = datetime.now()
        expires_at = now + timedelta(hours=24)

        session = ChunkSession(
            session_id=session_id,
            filename=request.filename,
            total_size=request.total_size,
            chunk_size=request.chunk_size,
            total_chunks=request.total_chunks,
            created_at=now,
            expires_at=expires_at,
        )

        cls._sessions[session_id] = session

        collector = MetricsCollector(
            method=UploadMethod.CHUNKED,
            file_size_bytes=request.total_size,
            run_id=run_id,
            iteration=iteration,
        )
        collector.start()
        collector.set_chunk_info(request.chunk_size, request.total_chunks)
        cls._collectors[session_id] = collector

        await cls._save_session(session, base_dir)

        logger.info(f"Chunk session created: {session_id} ({request.total_chunks} chunks)")

        return ChunkSessionResponse(
            session_id=session_id,
            filename=request.filename,
            total_size=request.total_size,
            chunk_size=request.chunk_size,
            total_chunks=request.total_chunks,
            created_at=now,
            expires_at=expires_at,
        )

    @classmethod
    async def upload_chunk(cls, session_id: str, chunk_number: int, chunk_data: bytes, base_dir: Path) -> ChunkUploadResponse:
        session = cls._sessions.get(session_id)

        if not session:
            session = await cls._load_session(session_id, base_dir)

            if not session:
                raise ValueError(f"Session not found: {session_id}")

            cls._sessions[session_id] = session

        chunk_dir = base_dir / 'chunked' / session_id
        chunk_dir.mkdir(parents=True, exist_ok=True)

        chunk_path = chunk_dir / f"chunk_{chunk_number:05d}"
        async with aiofiles.open(chunk_path, "wb") as f:
            await f.write(chunk_data)

        if chunk_number not in session.uploaded_chunks:
            session.uploaded_chunks.append(chunk_number)
            session.uploaded_size += len(chunk_data)

        await cls._save_session(session, base_dir)

        collector = cls._collectors.get(session_id)
        if collector:
            collector.sample()

        remaining = session.total_chunks - len(session.uploaded_chunks)

        logger.debug(f"Chunk {chunk_number}/{session.total_chunks} uploaded for session {session_id}")

        return ChunkUploadResponse(
            session_id=session_id,
            chunk_number=chunk_number,
            received_size=len(chunk_data),
            total_received=session.uploaded_size,
            remaining_chunks=remaining,
        )

    @classmethod
    async def get_status(cls, session_id: str, base_dir: Path) -> ChunkStatusResponse:
        '''세션 상태 조회'''
        session = cls._sessions.get(session_id)
        if not session:
            session = await cls._load_session(session_id, base_dir)
            if not session:
                raise ValueError(f"Session not found: {session_id}")

        all_chunks = set(range(1, session.total_chunks + 1))
        uploaded = set(session.uploaded_chunks)
        remaining = sorted(all_chunks - uploaded)

        progress = (len(uploaded) / session.total_chunks) * 100 if session.total_chunks > 0 else 0

        return ChunkStatusResponse(
            session_id=session_id,
            filename=session.filename,
            total_chunks=session.total_chunks,
            uploaded_chunks=sorted(session.uploaded_chunks),
            remaining_chunks=remaining,
            total_size=session.total_size,
            uploaded_size=session.uploaded_size,
            progress_percent=progress,
        )

    @classmethod
    async def complete(cls, session_id: str, base_dir: Path) -> ChunkCompleteResponse:
        '''청크 업로드 완료 및 병합'''
        session = cls._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if len(session.uploaded_chunks) != session.total_chunks:
            missing = session.total_chunks - len(session.uploaded_chunks)
            raise ValueError(f"Missing {missing} chunks")

        file_id = str(uuid.uuid4())
        final_path = base_dir / 'chunked' / f"{file_id}_{session.filename}"
        chunk_dir = base_dir / 'chunked' / session_id

        async with aiofiles.open(final_path, "wb") as outfile:
            for i in range(1, session.total_chunks + 1):
                chunk_path = chunk_dir / f"chunk_{i:05d}"
                async with aiofiles.open(chunk_path, "rb") as infile:
                    content = await infile.read()
                    await outfile.write(content)

        collector = cls._collectors.get(session_id)
        if collector:
            collector.stop()
            metrics = collector.build_metrics()

        else:
            from app.utils import MetricsCollector
            collector = MetricsCollector(UploadMethod.CHUNKED, session.total_size)
            collector.start()
            collector.stop()
            metrics = collector.build_metrics()

        import shutil
        shutil.rmtree(chunk_dir, ignore_errors=True)

        session_file = base_dir / 'sessions' / f"{session_id}.json"
        session_file.unlink(missing_ok=True)

        cls._sessions.pop(session_id, None)
        cls._collectors.pop(session_id, None)

        logger.info(f"Chunk upload completed: {file_id} ({session.total_chunks} chunks merged)")

        return ChunkCompleteResponse(
            filename=session.filename,
            total_size=session.total_size,
            total_chunks=session.total_chunks,
            metrics=metrics,
        )

    @classmethod
    async def _save_session(cls, session: ChunkSession, base_dir: Path) -> None:
        '''세션 파일 저장'''
        session_dir = base_dir / 'sessions' / f"{session.session_id}.json"
        async with aiofiles.open(session_dir, "w") as f:
            await f.write(json.dumps(session.to_dict()))

    @classmethod
    async def _load_session(cls, session_id: str, base_dir: Path) -> ChunkSession:
        '''세션 로드'''
        session_path = base_dir / 'sessions' / f"{session_id}.json"

        if not session_path.exists():
            return None

        async with aiofiles.open(session_path, "r") as f:
            data = json.loads(await f.read())
            return ChunkSession.from_dict(data)