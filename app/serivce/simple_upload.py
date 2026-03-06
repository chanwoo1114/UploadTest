from app.schema.upload_schema import UploadMethod, UploadResponse
from app.utils.metrices import MetricsCollector, track_metrics

from pathlib import Path
from fastapi import UploadFile
import aiofiles

class SimpleUploadService:
    '''일반 업로드'''
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload(self, file: UploadFile):
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        save_path = self.upload_dir / Path(file.filename)

        async with track_metrics(UploadMethod.SIMPLE, file_size) as collector:
            content = await file.read()

            async with aiofiles.open(save_path, 'wb') as f:
                await f.write(content)


