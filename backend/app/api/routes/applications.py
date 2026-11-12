from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from ...services import application_service as svc
from ...services import scoring_service
from ..schemas.application import NoteIn

router = APIRouter(tags=["applications"])


@router.get("/applications")
def list_applications(q: str | None = None, tier: Literal["Low", "Medium", "High"] | None = None,
                      channel: Literal["web", "mobile", "branch", "partner"] | None = None,
                      sort: Literal["score", "timestamp", "income", "credit"] = "timestamp",
                      order: Literal["asc", "desc"] = "desc",
                      page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    items, total = svc.list_applications(q=q, tier=tier, channel=channel, sort=sort, order=order,
                                         page=page, page_size=page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/applications/{application_id}")
def get_application(application_id: str):
    a = svc.get_application(application_id)
    if a is None:
        raise HTTPException(404, f"Application {application_id} not found")
    return a


@router.get("/applications/{application_id}/explanation")
def explanation(application_id: str):
    s = scoring_service.stored_score(application_id)
    if s is None:
        raise HTTPException(404, f"No score for application {application_id}")
    return {"application_id": application_id, "top_factors": s["top_factors"], "tier": s["tier"],
            "note": "Factors are model associations, not proof or causal explanations."}


@router.post("/applications/{application_id}/notes")
def add_note(application_id: str, body: NoteIn):
    if svc.get_application(application_id) is None:
        raise HTTPException(404, f"Application {application_id} not found")
    return {"notes": svc.add_note(application_id, body.note)}


@router.get("/overview")
def overview():
    from ...db.repositories import ApplicationRepository
    repo = ApplicationRepository()
    o = repo.overview()
    items, _ = repo.list(sort="score", order="desc", page=1, page_size=8)
    o["top_cases"] = items
    return o
