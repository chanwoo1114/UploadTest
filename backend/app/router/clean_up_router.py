from fastapi import APIRouter, HTTPException
import logging

from app.utils.clean_up import clean_up_all_files

logger = logging.getLogger(__name__)

admin_router = APIRouter(
    prefix="/cleanup",
    tags=["cleanup"]
)

@admin_router.post("", description="모든 파일 정리 API")
async def cleanup():
    '''모든 파일 정리'''
    try:
        result = await clean_up_all_files()
        total = sum(result.values())
        return {"message": f"Cleaned up {total} items", "data": result}

    except Exception as e:
        logger.error(f"Manual cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
