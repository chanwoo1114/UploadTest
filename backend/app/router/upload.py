from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path
import logging

from app.service.simple_upload import SimpleUploadService
from app.schema.upload_schema import (
    UploadResponse
)

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