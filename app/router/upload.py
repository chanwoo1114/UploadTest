from fastapi import APIRouter, File, UploadFile
from pathlib import Path

from app.service.simple_upload import SimpleUploadService


BASE_DIR = Path(__file__).resolve().parent.parent / "output"

simple_service = SimpleUploadService(BASE_DIR)

simple_router = APIRouter(prefix="/api/simple", tags=["Simple Upload"])

@simple_router.post("/upload")
async def simple_upload(file: UploadFile = File(...)):
    """일반 업로드"""
    return await simple_service.upload(file)

