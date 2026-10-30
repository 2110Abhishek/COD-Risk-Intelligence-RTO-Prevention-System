from datetime import datetime
from fastapi import APIRouter
from app.core.settings import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "timezone": settings.timezone,
        "timestamp": datetime.utcnow().isoformat(),
        "llm_enabled": settings.llm_enabled,
    }
