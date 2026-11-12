from __future__ import annotations

import networkx as nx


def entity_summary(g: nx.Graph, nid: str) -> dict:
    kind = g.nodes[nid]["kind"]
    comp = nx.node_connected_component(g, nid)
    apps = [n for n in g.neighbors(nid) if g.nodes[n]["kind"] == "application"]
    return {
        "entity_id": nid, "kind": kind, "label": g.nodes[nid]["label"], "degree": g.degree(nid),
        "linked_applications": len(apps), "component_size": len(comp),
    }


def neighborhood(g: nx.Graph, nid: str, radius: int = 2, max_nodes: int = 80) -> nx.Graph:
    sub = nx.ego_graph(g, nid, radius=radius)
    if sub.number_of_nodes() > max_nodes:
        keep = [nid] + sorted((n for n in sub if n != nid), key=lambda n: -g.degree(n))[: max_nodes - 1]
        sub = sub.subgraph(keep).copy()
    return sub


def linked_entities(g: nx.Graph, application_id: str) -> list[dict]:
    """Entities used by an application with how many OTHER applications share each."""
    nid = f"application:{application_id}"
    if nid not in g:
        return []
    out = []
    for n in g.neighbors(nid):
        k = g.nodes[n]["kind"]
        if k in ("applicant",):
            continue
        out.append({"entity_id": n, "kind": k, "label": g.nodes[n]["label"],
                    "shared_with_other_applications": g.degree(n) - 1})
    return out
