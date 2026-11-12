from __future__ import annotations

import networkx as nx


def to_react_flow(sub: nx.Graph, focus: str | None = None, flagged: set[str] | None = None) -> dict:
    flagged = flagged or set()
    nodes = [
        {"id": n, "type": d["kind"], "label": d["label"], "is_focus": n == focus,
         "flagged": n in flagged, "degree": sub.degree(n)}
        for n, d in sub.nodes(data=True)
    ]
    edges = [{"id": f"{a}|{b}", "source": a, "target": b, "relation": d.get("relation", "")}
             for a, b, d in sub.edges(data=True)]
    return {"nodes": nodes, "edges": edges,
            "note": "Connections are investigation signals, not proof of fraud."}
