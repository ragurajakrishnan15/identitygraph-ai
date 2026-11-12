from __future__ import annotations

import threading

import networkx as nx

from identitygraph.graph.analytics import entity_summary, linked_entities, neighborhood
from identitygraph.graph.builder import build_graph
from identitygraph.graph.serialization import to_react_flow

from ..db.repositories import ApplicationRepository

_lock = threading.Lock()
_graph: nx.Graph | None = None


def invalidate():
    global _graph
    _graph = None


def add_rows(df) -> None:
    """Incrementally add newly scored applications to the cached graph."""
    g = get_graph()
    with _lock:
        g.update(build_graph(df))


def get_graph() -> nx.Graph:
    global _graph
    with _lock:
        if _graph is None:
            _graph = build_graph(ApplicationRepository().all_frame())
        return _graph


def search_entities(q: str, limit: int = 15) -> list[dict]:
    g = get_graph()
    q = q.lower()
    out = []
    for n, d in g.nodes(data=True):
        if d["kind"] != "applicant" and q in n.lower():
            out.append({"entity_id": n, "kind": d["kind"], "label": d["label"], "degree": g.degree(n)})
            if len(out) >= limit:
                break
    return out


def top_hubs(limit: int = 10) -> list[dict]:
    g = get_graph()
    hubs = [(n, g.degree(n)) for n, d in g.nodes(data=True) if d["kind"] in ("device", "ip", "phone", "address", "email")]
    hubs.sort(key=lambda x: -x[1])
    return [{"entity_id": n, "kind": g.nodes[n]["kind"], "label": g.nodes[n]["label"], "degree": d}
            for n, d in hubs[:limit]]


def network(entity_id: str, radius: int = 2) -> dict | None:
    g = get_graph()
    if entity_id not in g:
        return None
    sub = neighborhood(g, entity_id, radius=radius)
    flagged = {n for n in sub if sub.nodes[n]["kind"] not in ("application", "applicant") and g.degree(n) >= 4}
    out = to_react_flow(sub, focus=entity_id, flagged=flagged)
    out["summary"] = entity_summary(g, entity_id)
    return out


def links_for_application(application_id: str) -> list[dict]:
    return linked_entities(get_graph(), application_id)
