from fastapi import APIRouter, HTTPException

from ...db.repositories import ModelRepository
from ...services import model_service, monitoring_service

router = APIRouter(tags=["models"])


@router.get("/models")
def models():
    return {"items": [{**m, "metrics": None} for m in ModelRepository().list()]}


@router.get("/metrics/model")
def metrics_model():
    try:
        return model_service.model_metrics()
    except FileNotFoundError as e:
        raise HTTPException(503, str(e)) from e


@router.get("/metrics/monitoring")
def metrics_monitoring():
    snap = monitoring_service.latest_snapshot()
    if snap is None:
        raise HTTPException(503, "No monitoring snapshot. Run scripts/evaluate.py then seed_db.py.")
    return snap


@router.get("/features")
def features():
    try:
        return model_service.feature_catalog()
    except FileNotFoundError as e:
        raise HTTPException(503, str(e)) from e
