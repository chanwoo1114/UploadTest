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



class ChunkUploadService:
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
    async def get_status(cls, session_id: str) -> ChunkStatusResponse:
        '''세션 상태 조회'''
        print(cls._sessions)
        session = cls._sessions.get(session_id)
        print(f"session:{session}" )


    @classmethod
    async def _save_session(cls, session: ChunkSession, base_dir: Path) -> None:
        '''세션 파일 저장'''
        session_dir = base_dir / 'sessions' / f"{session.session_id}.json"
        async with aiofiles.open(session_dir, "w") as f:
            await f.write(json.dumps(session.to_dict()))

