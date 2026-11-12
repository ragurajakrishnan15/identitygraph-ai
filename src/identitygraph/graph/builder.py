"""NetworkX identity graph. Edges are investigation signals, NOT proof of fraud."""
from __future__ import annotations

import networkx as nx
import pandas as pd

ENTITY_TYPES = {"device_id": "device", "ip_address": "ip", "email": "email", "phone": "phone", "address": "address"}


def node_id(kind: str, value: str) -> str:
    return f"{kind}:{value}"


def build_graph(df: pd.DataFrame) -> nx.Graph:
    g = nx.Graph()
    for row in df.itertuples(index=False):
        app = node_id("application", row.application_id)
        apl = node_id("applicant", row.applicant_id)
        g.add_node(app, kind="application", label=row.application_id)
        g.add_node(apl, kind="applicant", label=row.applicant_id)
        g.add_edge(apl, app, relation="submitted")
        for col, kind in ENTITY_TYPES.items():
            val = getattr(row, col)
            nid = node_id(kind, val)
            g.add_node(nid, kind=kind, label=str(val))
            g.add_edge(app, nid, relation="used" if kind in ("device", "ip") else "associated_with")
    return g
