from app.schema.upload_schema import UploadMethod, UploadResponse
from app.utils.metrics import track_metrics

import uuid
import logging
from pathlib import Path
from fastapi import UploadFile
import asyncio
import shutil

logger = logging.getLogger(__name__)

class SimpleUploadService:
    '''Simple Upload Service - 한 번에 전체 파일 전송'''

    @staticmethod
    async def upload(
        file: UploadFile,
        upload_dir: Path,
        run_id: str = "",
        iteration: int = 1
    ) -> UploadResponse:
        filename = file.filename or "unknown"

        # 파일 크기 확인 (복사 없이)
        await file.seek(0)
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        logger.info(f"Simple upload started: {filename} ({file_size} bytes)")

        async with track_metrics(UploadMethod.SIMPLE, file_size, run_id, iteration) as collector:
            file_id = str(uuid.uuid4())
            file_path = upload_dir / f"{file_id}_{filename}"

            def _copy():
                with open(file_path, "wb") as dst:
                    shutil.copyfileobj(file.file, dst)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _copy)

            collector.mark_upload_done()
            metrics = collector.build_metrics()

        logger.info(f"Simple upload completed: {file_id} in {metrics.time.total_sec:.3f}s")

        return UploadResponse(filename=filename, metrics=metrics)
