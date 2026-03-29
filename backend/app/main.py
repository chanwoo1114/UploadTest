import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.router.upload import (
    simple_router,
    streaming_router,
    chunked_router,

)
from app.router.clean_up_router import admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

UPLOAD_DIRS = [
    "uploads/simple",
    "uploads/chunked",
    "uploads/streaming",
    "uploads/s3",
    "uploads/benchmark",
    "uploads/sessions",
    "uploads/history",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    '''FastAPI 시작, 종료시 실행'''
    for dir_path in UPLOAD_DIRS:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    logger.info("Upload directories initialized")
    logger.info("Application started")

    yield

    logger.info("Application shutdown")



app = FastAPI(
    title="Upload Benchmark API",
    description="파일 업로드 방식별 성능 비교 API",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simple_router)
app.include_router(streaming_router)
app.include_router(chunked_router)
app.include_router(admin_router)