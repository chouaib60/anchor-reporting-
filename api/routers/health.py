from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()

@router.get("/")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@router.get("/ready")
async def readiness():
    return {
        "status": "ok",
        "checks": {"database": "not_checked", "minio": "not_checked"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }