from app.schema.upload_schema import UploadMethod, StreamingUploadResponse
from app.utils.metrics import track_metrics, ProgressTracker

import uuid
import logging
import aiofiles
from pathlib import Path
from fastapi import Request

logger = logging.getLogger(__name__)

class StreamingUploadService:
    '''Streaming Upload Service - Request body 직접 스트리밍'''

    @staticmethod
    async def stream_upload(
        request: Request,
        filename: str,
        size: int,
        upload_dir: Path,
        run_id: str = "",
        iteration: int = 1
    ) -> StreamingUploadResponse:
        file_id = str(uuid.uuid4())
        file_path = upload_dir / filename

        logger.info(f"Streaming upload started: {filename} (expected {size} bytes)")

        async with track_metrics(UploadMethod.STREAMING, size, run_id, iteration) as collector:
            tracker = ProgressTracker(size, collector)
            total_received = 0

            async with aiofiles.open(file_path, 'wb') as f:
                async for chunk in request.stream():
                    await f.write(chunk)
                    total_received += len(chunk)
                    tracker.update(len(chunk))

            collector.mark_upload_done()
            collector.sample()

            collector.file_size_bytes = total_received
            metrics = collector.build_metrics()

        logger.info(f"Streaming upload completed: {file_id} ({total_received} bytes)")

        return StreamingUploadResponse(
            filename=filename,
            file_size=total_received,
            metrics=metrics,
        )