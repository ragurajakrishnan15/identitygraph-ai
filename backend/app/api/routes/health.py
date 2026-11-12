from fastapi import APIRouter, HTTPException

from ...services.model_service import ready

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/health/ready")
def health_ready():
    if not ready():
        raise HTTPException(503, "Model artifact not found. Run scripts/train.py.")
    return {"status": "ready"}
