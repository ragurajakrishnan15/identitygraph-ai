"""Build the NetworkX identity graph and print summary statistics."""
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from identitygraph.data.ingestion import load_applications  # noqa: E402
from identitygraph.graph.builder import build_graph  # noqa: E402

if __name__ == "__main__":
    g = build_graph(load_applications())
    comps = sorted((len(c) for c in nx.connected_components(g)), reverse=True)
    print(f"nodes={g.number_of_nodes()} edges={g.number_of_edges()} components={len(comps)} largest={comps[:5]}")
