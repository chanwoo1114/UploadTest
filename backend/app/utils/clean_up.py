import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

UPLOAD_ROOT = Path("uploads")

CLEANUP_TARGETS = ["simple", "streaming", "chunked", "s3", "benchmark", "sessions"]


async def clean_up_all_files() -> dict[str, int]:
    '''모든 업로드 디렉토리 내 파일/폴더 삭제'''
    result: dict[str, int] = {}

    for dir_name in CLEANUP_TARGETS:
        target_dir = UPLOAD_ROOT / dir_name
        if not target_dir.exists():
            continue

        deleted = 0
        for item in target_dir.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                deleted += 1
            except Exception as e:
                logger.warning(f"Failed to delete {item}: {e}")

        if deleted > 0:
            result[dir_name] = deleted
            logger.info(f"Cleaned up {deleted} items from {dir_name}/")

    return result