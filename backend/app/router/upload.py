from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from pathlib import Path
import logging

from app.service.chunk_upload import ChunkedUploadService
from app.service.simple_upload import SimpleUploadService
from app.schema.upload_schema import (
    UploadResponse,
    StreamingUploadResponse,
    ChunkSessionRequest,
    ChunkSessionResponse,
    ChunkUploadResponse,
    ChunkStatusResponse,
    ChunkCompleteResponse,
    MultipartInitResponse,
    MultipartInitRequest,
    PartUploadResponse,
)
from app.service.streaming_upload import StreamingUploadService
from app.service.multipart_upload import MultipartUploadService

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent.parent / "uploads"


simple_router = APIRouter(prefix="/simple", tags=["Simple Upload"])

'''심플 업로드'''
@simple_router.post("/upload", response_model=UploadResponse)
async def simple_upload(file: UploadFile = File(...)):
    '''Simple 업로드 - 파일 전체를 한 번에 전송'''
    try:
        upload_dir = BASE_DIR / "simple"
        return await SimpleUploadService.upload(file, upload_dir)
    except Exception as e:
        logger.error(f"Simple upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

'''스트리밍 업로드'''
streaming_router = APIRouter(prefix="/streaming", tags=["Streaming Upload"])
@streaming_router.post("/upload", response_model=StreamingUploadResponse)
async def streaming_upload(request: Request, filename: str, size: int):
    '''Streaming 업로드 - Request body 직접 스트리밍'''
    try:
        upload_dir = BASE_DIR / "streaming"
        return await StreamingUploadService.stream_upload(request, filename, size, upload_dir)

    except Exception as e:
        logger.error(f"Streaming upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

'''청크 세션 생성'''
chunked_router = APIRouter(prefix="/chunk", tags=["Chunk Upload"])

@chunked_router.post("/sessions", response_model=ChunkSessionResponse)
async def create_chunk_session(request: ChunkSessionRequest):
    '''청크 업로드 세션 생성'''
    try:
        return await ChunkedUploadService.create_session(request, BASE_DIR)
    except Exception as e:
        logger.error(f"Failed to create chunk session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chunked_router.post("/sessions/{session_id}/chunks/{chunk_number}", response_model=ChunkUploadResponse)
async def upload_chunk(
    session_id: str,
    chunk_number: int,
    chunk: UploadFile = File(...)
):
    '''청크 업로드'''
    try:
        chunk_data = await chunk.read()
        return await ChunkedUploadService.upload_chunk(session_id, chunk_number, chunk_data, BASE_DIR)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Chunk upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chunked_router.get("/sessions/{session_id}/status", response_model=ChunkStatusResponse)
async def get_chunk_status(session_id: str):
    '''청크 세션 상태 조회'''
    try:
        return await ChunkedUploadService.get_status(session_id, BASE_DIR)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to get chunk status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@chunked_router.post("/sessions/{session_id}/complete", response_model=ChunkCompleteResponse)
async def complete_chunk_upload(session_id: str):
    '''청크 업로드 완료'''
    try:
        return await ChunkedUploadService.complete(session_id, BASE_DIR)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to complete chunk upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

multipart_router = APIRouter(prefix="/multipart", tags=["Multipart Upload"])

@multipart_router.post("/init", response_model=MultipartInitResponse)
async def init_multipart_upload(request: MultipartInitRequest):
    '''멀티파트 업로드 초기화'''
    try:
        return await MultipartUploadService.init_upload(request)
    except Exception as e:
        logger.error(f"Failed to init multipart upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@multipart_router.post("/{upload_id}/parts/{part_number}", response_model=PartUploadResponse)
async def upload_part(
    upload_id: str,
    part_number: int,
    part: UploadFile = File(...)
):
    '''파트 업로드'''
    try:
        part_data = await part.read()
        return await MultipartUploadService.upload_part(upload_id, part_number, part_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Part upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))