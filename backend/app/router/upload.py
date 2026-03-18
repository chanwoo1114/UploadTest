from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from pathlib import Path
import logging

from app.service.simple_upload import SimpleUploadService
from app.schema.upload_schema import (
    UploadResponse,
    StreamingUploadResponse
)
from app.service.streaming_upload import StreamingUploadService

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent.parent / "uploads"


simple_router = APIRouter(prefix="/simple", tags=["Simple Upload"])

@simple_router.post("/upload", response_model=UploadResponse)
async def simple_upload(file: UploadFile = File(...)):
    '''Simple 업로드 - 파일 전체를 한 번에 전송'''
    try:
        upload_dir = BASE_DIR / "simple"
        return await SimpleUploadService.upload(file, upload_dir)
    except Exception as e:
        logger.error(f"Simple upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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