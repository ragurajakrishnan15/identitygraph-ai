from fastapi import APIRouter, HTTPException

from ...services import scoring_service
from ..schemas.application import ApplicationIn
from ..schemas.scoring import BatchScoreRequest, ScoreResponse

router = APIRouter(tags=["scoring"])


@router.post("/score", response_model=ScoreResponse)
def score(app: ApplicationIn):
    try:
        return scoring_service.score_payloads([app.model_dump()])[0]
    except ValueError as e:
        raise HTTPException(409, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(503, str(e)) from e


@router.post("/score/batch", response_model=list[ScoreResponse])
def score_batch(req: BatchScoreRequest):
    try:
        return scoring_service.score_payloads([a.model_dump() for a in req.applications])
    except ValueError as e:
        raise HTTPException(409, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(503, str(e)) from e
