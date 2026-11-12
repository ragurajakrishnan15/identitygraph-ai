import numpy as np
import pytest

from identitygraph.decisioning.policy import display_score, tier_for
from identitygraph.evaluation.metrics import compute_metrics, precision_at_budget, recall_at_fpr
from identitygraph.graph.analytics import entity_summary, linked_entities
from identitygraph.graph.builder import build_graph
from identitygraph.graph.serialization import to_react_flow
from identitygraph.models.thresholds import select_thresholds
from identitygraph.monitoring.drift import psi


def test_graph_structure(small_df):
    g = build_graph(small_df.head(300))
    kinds = {d["kind"] for _, d in g.nodes(data=True)}
    assert {"application", "applicant", "device", "ip", "email", "phone", "address"} <= kinds
    app = f"application:{small_df.application_id.iloc[0]}"
    assert len(linked_entities(g, small_df.application_id.iloc[0])) == 5
    dev = f"device:{small_df.device_id.iloc[0]}"
    assert entity_summary(g, dev)["linked_applications"] >= 1
    out = to_react_flow(g.subgraph([app, dev]).copy(), focus=app)
    assert "not proof" in out["note"] and len(out["nodes"]) == 2


def test_metrics_known_values():
    y = np.array([0, 0, 0, 0, 1, 1, 1, 0, 0, 1])
    s = np.array([.1, .2, .3, .4, .9, .8, .7, .35, .15, .6])
    m = compute_metrics(y, s, 0.5)
    assert m["roc_auc"] == pytest.approx(1.0) and m["pr_auc"] == pytest.approx(1.0)
    assert m["confusion_matrix"] == {"tn": 6, "fp": 0, "fn": 0, "tp": 4}
    assert recall_at_fpr(y, s, 0.01) == pytest.approx(1.0)
    assert precision_at_budget(y, s, 0.3) == 1.0


def test_policy_thresholds():
    t = {"medium": 0.3, "high": 0.6}
    assert tier_for(0.1, t) == "Low" and tier_for(0.3, t) == "Medium" and tier_for(0.6, t) == "High"
    assert display_score(0.456) == 46 and display_score(2) == 100


def test_thresholds_selected_from_validation_only():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 400)
    s = np.clip(y * 0.4 + rng.random(400) * 0.6, 0, 1)
    t = select_thresholds(y, s)
    assert t["selected_on"] == "validation" and t["medium"] <= t["high"]


def test_psi_identical_is_zero_and_shift_is_large():
    rng = np.random.default_rng(1)
    a = rng.normal(size=5000)
    assert psi(a, a) < 1e-6
    assert psi(a, a + 2) > 0.25
