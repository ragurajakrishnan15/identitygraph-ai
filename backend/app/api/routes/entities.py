from fastapi import APIRouter, HTTPException, Query

from ...services import graph_service

router = APIRouter(tags=["entities"])


@router.get("/entities")
def search(q: str = Query("", description="substring of entity id"), limit: int = Query(15, ge=1, le=50)):
    if not q:
        return {"items": graph_service.top_hubs(limit), "note": "Highest-degree shared identifiers"}
    return {"items": graph_service.search_entities(q, limit)}


@router.get("/entities/{entity_id:path}/network")
def entity_network(entity_id: str, radius: int = Query(2, ge=1, le=3)):
    res = graph_service.network(entity_id, radius)
    if res is None:
        raise HTTPException(404, f"Entity {entity_id} not found")
    return res
