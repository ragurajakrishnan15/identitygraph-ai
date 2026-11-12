from __future__ import annotations

from functools import lru_cache

from identitygraph.features.pipeline import BASE_FEATURES, GRAPH_FEATURES
from identitygraph.models.registry import load_bundle, load_json

FEATURE_GROUPS = {
    "Device / IP / contact reuse": [f for f in BASE_FEATURES if "prior" in f],
    "Application velocity": [f for f in BASE_FEATURES if "apps_" in f],
    "Identity consistency": ["email_name_mismatch", "young_high_credit", "age"],
    "Financial": ["income_to_credit_ratio", "log_income", "log_requested_credit"],
    "Temporal": ["hour", "day_of_week", "is_night"],
    "Graph": GRAPH_FEATURES,
}


@lru_cache
def get_bundle() -> dict:
    return load_bundle()


def model_metrics() -> dict:
    return load_json("metrics.json")


def feature_catalog() -> dict:
    imp = {r["feature"]: r["importance"]
           for r in model_metrics()["models"]["graph_gradient_boosting"]["feature_importance"]}
    return {"groups": [{"group": g, "features": [{"name": f, "importance": imp.get(f)} for f in fs]}
                       for g, fs in FEATURE_GROUPS.items()]}


def ready() -> bool:
    try:
        get_bundle()
        return True
    except FileNotFoundError:
        return False
